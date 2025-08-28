import asyncio
import json
import os
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
import structlog
from a2a.client import (
    A2ACardResolver,
    A2AClient,
    A2AClientError,
    A2AClientHTTPError,
    A2AClientJSONError,
)
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    DataPart,
    FilePart,
    FileWithUri,
    InternalError,
    InvalidAgentResponseError,
    JSONRPCErrorResponse,
    Message,
    MessageSendConfiguration,
    MessageSendParams,
    Part,
    Role,
    SendStreamingMessageRequest,
    SendStreamingMessageResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)

from rasa.agents.constants import (
    A2A_AGENT_CONTEXT_ID_KEY,
    A2A_AGENT_TASK_ID_KEY,
    AGENT_DEFAULT_MAX_RETRIES,
    AGENT_DEFAULT_TIMEOUT_SECONDS,
    AGENT_METADATA_TOOL_RESULTS_KEY,
    MAX_AGENT_RETRY_DELAY_SECONDS,
)
from rasa.agents.core.agent_protocol import AgentProtocol
from rasa.agents.core.types import AgentStatus, ProtocolType
from rasa.agents.schemas import AgentInput, AgentOutput
from rasa.core.available_agents import AgentConfig
from rasa.shared.exceptions import (
    AgentInitializationException,
    InvalidParameterException,
    RasaException,
)

structlogger = structlog.get_logger()


class A2AAgent(AgentProtocol):
    """A2A client implementation"""

    def __init__(
        self,
        name: str,
        description: str,
        agent_card_path: str,
        timeout: int,
        max_retries: int,
    ) -> None:
        self._name = name
        self._description = description
        self._agent_card_path = agent_card_path
        self._timeout = timeout
        self._max_retries = max_retries

        self.agent_card: Optional[AgentCard] = None
        self._client: Optional[A2AClient] = None

    @classmethod
    def from_config(cls, config: AgentConfig) -> AgentProtocol:
        """Initialize the A2A Agent with the given configuration."""
        agent_card_path = (
            config.configuration.agent_card if config.configuration else None
        )
        if not agent_card_path:
            raise InvalidParameterException(
                "Agent card path or URL must be provided in the configuration "
                "for A2A agents."
            )

        timeout = (
            config.configuration.timeout
            if config.configuration and config.configuration.timeout
            else AGENT_DEFAULT_TIMEOUT_SECONDS
        )
        max_retries = (
            config.configuration.max_retries
            if config.configuration and config.configuration.max_retries
            else AGENT_DEFAULT_MAX_RETRIES
        )

        return cls(
            name=config.agent.name,
            description=config.agent.description,
            agent_card_path=agent_card_path,
            timeout=timeout,
            max_retries=max_retries,
        )

    @property
    def protocol_type(self) -> ProtocolType:
        return ProtocolType.A2A

    async def connect(self) -> None:
        """Fetch the AgentCard and initialize the A2A client."""
        from rasa.nlu.utils import is_url

        if is_url(self._agent_card_path):
            self.agent_card = await A2AAgent._resolve_agent_card_with_retry(
                self._agent_card_path, self._timeout, self._max_retries
            )
        else:
            self.agent_card = A2AAgent._load_agent_card_from_file(self._agent_card_path)
        structlogger.debug(
            "a2a_agent.from_config",
            event_info=f"Loaded agent card from {self._agent_card_path}",
            agent_card=self.agent_card,
        )

        try:
            self._client = A2AClient(
                httpx.AsyncClient(timeout=self._timeout), agent_card=self.agent_card
            )
            structlogger.debug(
                "a2a_agent.connect.success",
                event_info=f"Connected to A2A server '{self._name}' "
                f"at {self.agent_card.url}",
            )
            # TODO: Make a test request to /tasks to verify the connection
        except Exception as exception:
            structlogger.error(
                "a2a_agent.connect.error",
                event_info="Failed to initialize A2A client",
                agent_name=self._name,
                error=str(exception),
            )
            raise AgentInitializationException(
                f"Failed to initialize A2A client for agent "
                f"'{self._name}': {exception}"
            ) from exception

    async def disconnect(self) -> None:
        """We don't need to explicitly disconnect the A2A client"""
        return

    async def process_input(self, agent_input: AgentInput) -> AgentInput:
        """Pre-process the input before sending it to the agent."""
        # A2A-specific input processing logic
        return agent_input

    async def run(self, agent_input: AgentInput) -> AgentOutput:
        """Send a message to Agent/server and return response."""
        if not self._client or not self.agent_card:
            structlogger.error(
                "a2a_agent.run.error",
                event_info="A2A client is not initialized. " "Call connect() first.",
            )
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.FATAL_ERROR,
                error_message="Client not initialized",
            )

        if self.agent_card.capabilities.streaming:
            structlogger.info(
                "a2a_agent.run.streaming",
                event_info="Running A2A agent in streaming mode",
                agent_name=self._name,
            )
            return await self._run_streaming_agent(agent_input)
        else:
            # we dont support non-streaming mode yet
            structlogger.error(
                "a2a_agent.run.error",
                event_info="Non-streaming mode is currently not supported",
                agent_name=self._name,
            )
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.FATAL_ERROR,
                error_message="Non-streaming mode is not supported",
            )

    async def process_output(self, output: AgentOutput) -> AgentOutput:
        """Post-process the output before returning it to Rasa."""
        # A2A-specific output processing logic
        return output

    async def _run_streaming_agent(self, agent_input: AgentInput) -> AgentOutput:
        if not self._client:
            structlogger.error(
                "a2a_agent.run_streaming_agent.error",
                event_info="A2A client is not initialized. Call connect() first.",
            )
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.FATAL_ERROR,
                error_message="Client not initialized",
            )
        message_send_params = self._prepare_message_send_params(agent_input)

        try:
            async for response in self._client.send_message_streaming(
                SendStreamingMessageRequest(
                    id=str(uuid.uuid4()), params=message_send_params
                )
            ):
                agent_output = self._handle_streaming_response(agent_input, response)
                if agent_output is not None:
                    return agent_output
                else:
                    # Not a terminal response, continue waiting for next responses
                    continue

        except A2AClientError as exception:
            structlogger.error(
                "a2a_agent.run_streaming_agent.error",
                event_info="Error during streaming message to A2A server",
                agent_name=self._name,
                error=str(exception),
            )
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.FATAL_ERROR,
                error_message=f"Streaming error: {exception!s}",
            )

        # In case we didn't receive any response or the response ended unexpectedly
        structlogger.error(
            "a2a_agent.run_streaming_agent.unexpected_end",
            event_info="Unexpected end of streaming response from A2A server",
            agent_name=self._name,
        )
        return AgentOutput(
            id=agent_input.id,
            status=AgentStatus.FATAL_ERROR,
            error_message="Unexpected end of streaming response",
        )

    def _handle_streaming_response(
        self, agent_input: AgentInput, response: SendStreamingMessageResponse
    ) -> Optional[AgentOutput]:
        """If the agent response is terminal (i.e., completed, failed, etc.),
        this method will return an AgentOutput.
        Otherwise, the task is still in progress (i.e., submitted, working), so this
        method will return None, so that the streaming or pooling agent can continue
        to wait for updates.
        """
        if isinstance(response.root, JSONRPCErrorResponse):
            return self._handle_json_rpc_error_response(agent_input, response.root)

        response_result = response.root.result
        if isinstance(response_result, Task):
            return self._handle_task_response(agent_input, response_result)
        elif isinstance(response_result, Message):
            return self._handle_message_response(response_result)
        elif isinstance(response_result, TaskStatusUpdateEvent):
            return self._handle_task_status_update_event(agent_input, response_result)
        elif isinstance(response_result, TaskArtifactUpdateEvent):
            return self._handle_task_artifact_update_event(agent_input, response_result)
        else:
            # Currently, no other response types exist, so this branch is
            # unreachable. It is kept as a safeguard against future changes
            # to the A2A protocol: if new response types are introduced,
            # the agent will log an error instead of crashing.
            return self._handle_unexpected_response_type(agent_input, response_result)

    def _handle_json_rpc_error_response(
        self, agent_input: AgentInput, response: JSONRPCErrorResponse
    ) -> AgentOutput:
        structlogger.error(
            "a2a_agent.run_streaming_agent.error",
            event_info="Received error response from A2A server during streaming",
            agent_name=self._name,
            error=str(response.error),
        )
        if isinstance(
            response.error,
            (
                InternalError,
                InvalidAgentResponseError,
            ),
        ):
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.RECOVERABLE_ERROR,
                error_message=str(response.error),
            )
        else:
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.FATAL_ERROR,
                error_message=str(response.error),
            )

    def _handle_task_response(
        self, agent_input: AgentInput, task: Task
    ) -> Optional[AgentOutput]:
        structlogger.debug(
            "a2a_agent.run_streaming_agent.task_received",
            event_info="Received task from A2A",
            agent_name=self._name,
            task=task,
        )
        agent_output = self._handle_task_status(
            agent_input=agent_input,
            context_id=task.context_id,
            task_id=task.id,
            task_status=task.status,
        )
        return agent_output

    def _handle_message_response(self, message: Message) -> Optional[AgentOutput]:
        # Message represents an intermediate conversational update,
        # we need to continue waiting for task updates
        structlogger.debug(
            "a2a_agent.run_streaming_agent.message_received",
            event_info="Received message from A2A",
            agent_name=self._name,
            message=message,
        )
        return None

    def _handle_task_status_update_event(
        self, agent_input: AgentInput, event: TaskStatusUpdateEvent
    ) -> Optional[AgentOutput]:
        structlogger.debug(
            "a2a_agent.run_streaming_agent.task_status_update_received",
            event_info="Received task status update from A2A",
            agent_name=self._name,
            task_status_update_event=event,
        )
        agent_output = self._handle_task_status(
            agent_input=agent_input,
            context_id=event.context_id,
            task_id=event.task_id,
            task_status=event.status,
        )
        return agent_output

    def _handle_task_artifact_update_event(
        self, agent_input: AgentInput, event: TaskArtifactUpdateEvent
    ) -> AgentOutput:
        structlogger.debug(
            "a2a_agent.run_streaming_agent.task_artifact_update_received",
            event_info="Received task artifact update from A2A",
            agent_name=self._name,
            task_artifact_update_event=event,
        )
        return AgentOutput(
            id=agent_input.id,
            status=AgentStatus.COMPLETED,
            response_message=self._generate_response_message_from_parts(
                event.artifact.parts
            ),
            tool_results=self._generate_tool_results_from_parts(
                agent_input, event.artifact.parts
            ),
        )

    def _handle_unexpected_response_type(
        self, agent_input: AgentInput, response_result: Any
    ) -> AgentOutput:
        structlogger.error(
            "a2a_agent.run_streaming_agent.unexpected_response_type",
            event_info="Received unexpected response type from A2A server "
            "during streaming",
            agent_name=self._name,
            response_type=type(response_result),
        )
        return AgentOutput(
            id=agent_input.id,
            status=AgentStatus.FATAL_ERROR,
            error_message=f"Unexpected response type: {type(response_result)}",
        )

    def _handle_task_status(
        self,
        agent_input: AgentInput,
        context_id: str,
        task_id: str,
        task_status: TaskStatus,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentOutput]:
        """If the task status is terminal (i.e., completed, failed, etc.),
        return an AgentOutput.
        If the task is still in progress (i.e., submitted, working), return None,
        so that the streaming or pooling agent can continue to wait for updates.
        """
        state = task_status.state

        metadata = metadata or {}
        metadata[A2A_AGENT_CONTEXT_ID_KEY] = context_id
        metadata[A2A_AGENT_TASK_ID_KEY] = task_id

        if state == TaskState.input_required:
            response_message = (
                self._generate_response_message_from_parts(task_status.message.parts)
                if task_status.message
                else ""
            )  # This should not happen, but as type of message property
            # is optional, so we need to handle it
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.INPUT_REQUIRED,
                response_message=response_message,
                metadata=metadata,
            )
        elif state == TaskState.completed:
            response_message = (
                self._generate_response_message_from_parts(task_status.message.parts)
                if task_status.message
                else ""
            )  # This should not happen, but as type of message property
            # is optional, so we need to handle it
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.COMPLETED,
                response_message=response_message,
                metadata=metadata,
            )
        elif (
            state == TaskState.failed
            or state == TaskState.canceled
            or state == TaskState.rejected
            or state == TaskState.auth_required
        ):
            structlogger.error(
                "a2a_agent.run_streaming_agent.unsuccessful_task_state",
                event_info="Task execution finished with an unsuccessful state",
                agent_name=self._name,
                state=state,
            )
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.RECOVERABLE_ERROR,
                error_message=f"Task state: {state}",
                metadata=metadata,
            )
        elif state == TaskState.submitted or state == TaskState.working:
            # The task is still in progress, return None to continue waiting for updates
            return None
        else:
            structlogger.error(
                "a2a_agent.run_streaming_agent.unexpected_task_state",
                event_info="Unexpected task state received from A2A",
                agent_name=self._name,
                state=state,
            )
            return AgentOutput(
                id=agent_input.id,
                status=AgentStatus.FATAL_ERROR,
                error_message=f"Unexpected task state: {state}",
                metadata=metadata,
            )

    @staticmethod
    def _prepare_message_send_params(agent_input: AgentInput) -> MessageSendParams:
        parts: List[Part] = []
        if agent_input.metadata and A2A_AGENT_CONTEXT_ID_KEY in agent_input.metadata:
            # Agent knows the conversation history already, send the last
            # user message only
            parts.append(Part(root=TextPart(text=agent_input.user_message)))
        else:
            # Send the full conversation history
            parts.append(Part(root=TextPart(text=agent_input.conversation_history)))

        if len(agent_input.slots) > 0:
            slots_dict: Dict[str, Any] = {
                "slots": [
                    slot.model_dump(exclude={"type", "allowed_values"})
                    for slot in agent_input.slots
                    if slot.value is not None
                ]
            }
            parts.append(Part(root=DataPart(data=slots_dict)))

        agent_message = Message(
            role=Role.user,
            parts=parts,
            message_id=str(uuid.uuid4()),
            context_id=agent_input.metadata.get(A2A_AGENT_CONTEXT_ID_KEY, None),
            task_id=agent_input.metadata.get(A2A_AGENT_TASK_ID_KEY, None),
        )
        structlogger.debug(
            "a2a_agent._prepare_message_send_params",
            event_info="Prepared message to send to A2A server",
            agent_name=agent_input.id,
            message=agent_message,
        )
        return MessageSendParams(
            message=agent_message,
            configuration=MessageSendConfiguration(
                accepted_output_modes=["text", "text/plain", "application/json"],
            ),
        )

    @staticmethod
    def _generate_response_message_from_parts(parts: Optional[List[Part]]) -> str:
        """Convert a list of Part objects to a single string message."""
        result = ""
        if not parts:
            return result
        for part in parts:
            if isinstance(part.root, TextPart):
                result += part.root.text + "\n"
            elif isinstance(part.root, DataPart):
                # DataPart results will be returned as a pert of the tool results,
                # we don't need to include it in the response message
                continue
            elif isinstance(part.root, FilePart) and isinstance(
                part.root.file, FileWithUri
            ):
                # If the file is a FileWithUri, we can include the URI
                result += f"File: {part.root.file.uri}\n"
            else:
                structlogger.warning(
                    "a2a_agent._parts_to_single_message.warning",
                    event_info="Unsupported part type encountered",
                    part_type=type(part.root),
                )
        return result.strip()

    @staticmethod
    def _generate_tool_results_from_parts(
        agent_input: AgentInput, parts: List[Part]
    ) -> Optional[List[List[Dict[str, Any]]]]:
        tool_results_of_current_iteration: List[Dict[str, Any]] = []
        for i, part in enumerate(parts):
            if (
                isinstance(part.root, DataPart)
                and part.root.data
                and len(part.root.data) > 0
            ):
                # There might be multiple DataParts in the response,
                # we will treat each of them as a separate tool result.
                # The tool name will be the agent ID + index of the part.
                tool_results_of_current_iteration.append(
                    {"tool_name": f"{agent_input.id}_{i}", "result": part.root.data}
                )

        previous_tool_results: List[List[Dict[str, Any]]] = (
            agent_input.metadata.get(AGENT_METADATA_TOOL_RESULTS_KEY, []) or []
        )
        previous_tool_results.append(tool_results_of_current_iteration)

        return previous_tool_results

    @staticmethod
    def _load_agent_card_from_file(agent_card_path: str) -> AgentCard:
        """Load agent card from JSON file."""
        try:
            with open(os.path.abspath(agent_card_path), "r") as f:
                card_data = json.load(f)

            skills = [
                AgentSkill(
                    id=skill_data["id"],
                    name=skill_data["name"],
                    description=skill_data["description"],
                    tags=skill_data.get("tags", []),
                    examples=skill_data.get("examples", []),
                )
                for skill_data in card_data.get("skills", [])
            ]

            return AgentCard(
                name=card_data["name"],
                description=card_data["description"],
                url=card_data["url"],
                version=card_data.get("version", "1.0.0"),
                default_input_modes=card_data.get(
                    "defaultInputModes", ["text", "text/plain"]
                ),
                default_output_modes=card_data.get(
                    "defaultOutputModes", ["text", "text/plain", "application/json"]
                ),
                capabilities=AgentCapabilities(
                    streaming=card_data.get("capabilities", {}).get("streaming", True)
                ),
                skills=skills,
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Agent card file not found: {agent_card_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in agent card file {agent_card_path}: {e}")
        except KeyError as e:
            raise ValueError(
                f"Missing required field in agent card {agent_card_path}: {e}"
            )

    @staticmethod
    async def _resolve_agent_card_with_retry(
        agent_card_path: str, timeout: int, max_retries: int
    ) -> AgentCard:
        """Resolve the agent card from a given path or URL."""
        # split agent_card_path into base URL and path
        try:
            url_parts = urlparse(agent_card_path)
            base_url = f"{url_parts.scheme}://{url_parts.netloc}"
            path = url_parts.path
        except ValueError:
            raise RasaException(f"Could not parse the URL: '{agent_card_path}'.")
        structlogger.debug(
            "a2a_agent.resolve_agent_card",
            event_info="Resolving agent card from remote URL",
            agent_card_path=agent_card_path,
            base_url=base_url,
            path=path,
            timeout=timeout,
        )

        for attempt in range(max_retries):
            if attempt > 0:
                structlogger.debug(
                    "a2a_agent.resolve_agent_card.retrying",
                    agent_card_path=f"{base_url}/{path}",
                    attempt=attempt + 1,
                    num_retries=max_retries,
                )

            try:
                agent_card = await A2ACardResolver(
                    httpx.AsyncClient(timeout=timeout),
                    base_url=base_url,
                    agent_card_path=path,
                ).get_agent_card()

                if agent_card:
                    return agent_card
            except (A2AClientHTTPError, A2AClientJSONError) as exception:
                structlogger.warning(
                    "a2a_agent.resolve_agent_card.error",
                    event_info="Error while resolving agent card",
                    agent_card_path=agent_card_path,
                    attempt=attempt + 1,
                    num_retries=max_retries,
                    error=str(exception),
                )
                if attempt < max_retries - 1:
                    # exponential backoff - wait longer with each retry
                    # 1 second, 2 seconds, 4 seconds, etc.
                    await asyncio.sleep(min(2**attempt, MAX_AGENT_RETRY_DELAY_SECONDS))

        raise AgentInitializationException(
            f"Failed to resolve agent card from {agent_card_path} after "
            f"{max_retries} attempts."
        )
