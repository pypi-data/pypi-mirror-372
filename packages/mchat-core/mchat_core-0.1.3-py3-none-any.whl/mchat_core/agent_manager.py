import asyncio
import json
import os
from collections.abc import AsyncIterable, Callable, Mapping, Sequence
from functools import reduce
from typing import (
    Any,
)

import yaml
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import (
    TaskResult,
    TerminatedException,
    TerminationCondition,
)
from autogen_agentchat.conditions import (
    ExternalTermination,
    MaxMessageTermination,
    StopMessageTermination,
    TextMentionTermination,
)
from autogen_agentchat.messages import (
    AgentEvent,
    ChatMessage,
    ModelClientStreamingChunkEvent,
    MultiModalMessage,
    StopMessage,
    TextMessage,
    ThoughtEvent,
    ToolCallExecutionEvent,
    ToolCallRequestEvent,
    ToolCallSummaryMessage,
    UserInputRequestedEvent,
)
from autogen_agentchat.teams import (
    MagenticOneGroupChat,
    RoundRobinGroupChat,
    SelectorGroupChat,
)
from autogen_core import CancellationToken
from autogen_core.model_context import UnboundedChatCompletionContext
from autogen_core.models import (
    AssistantMessage,
    SystemMessage,
    UserMessage,
)
from autogen_core.tools import FunctionTool
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_ext.models.openai._openai_client import (
    AzureOpenAIChatCompletionClient,
    OpenAIChatCompletionClient,
)

from .logging_utils import get_logger, trace  # noqa: F401
from .model_manager import ModelManager
from .terminator import SmartReflectorTermination
from .tool_utils import load_tools

logger = get_logger(__name__)


label_prompt = (
    "Here is a conversation between a Human and AI. Give me no more than 10 words which"
    " will be used to remind the user of the conversation.  Your reply should be no"
    " more than 10 words and at most 66 total characters. Here is the conversation"
    " {conversation}"
)

summary_prompt = (
    "Here is a conversation between a Human and AI. Provide a detailed summary of the "
    "Conversation: "
    "{conversation}"
)


class IsCompleteTermination(TerminationCondition):
    mm = ModelManager()
    memory_model = mm.open_model(mm.default_memory_model)
    prompt = """ Take a look at the conversation so far. If the conversation has
    reached a natural conclusion and it is the clear that the agent had completed
    the task and has provided a clear response, return True. Otherwise, return False.
    ONLY return the word 'True' or 'False'.  Here is the conversation so far:
    {conversation}"""

    def __init__(self):
        self._is_terminated = False

    @property
    def terminated(self) -> bool:
        return self._is_terminated

    async def __call__(
        self, messages: Sequence[AgentEvent | ChatMessage]
    ) -> StopMessage | None:
        if self._is_terminated:
            raise TerminatedException("Termination condition has already been reached")
        system_message = IsCompleteTermination.prompt.format(conversation=messages)
        out = await IsCompleteTermination.memory_model.create(
            [SystemMessage(content=system_message)]
        )
        logger.debug(f"IsCompleteTermination response: {out.content.strip()}")
        if out.content.strip().lower() == "true":
            self._is_terminated = True
            return StopMessage(
                content="Agent is complete termination condition met",
                source="IsCompleteTermination",
            )
        return None

    async def reset(self):
        self._is_terminated = False


class AutogenManager:
    # createa a model_manager for use with llmtools and AutogenManager
    ag_mm = ModelManager()
    ag_memory_model = ag_mm.open_model(ag_mm.default_memory_model)

    def __init__(
        self,
        message_callback: Callable | None = None,
        agents: dict | None = None,
        agent_paths: list[str] | None = None,
        stream_tokens: bool = None,
        tools_directory: str | None = None,
        load_default_tools: bool = True,
    ):
        # Ensure that exactly one of agents or agent_paths is provided
        if (agents is None) == (
            agent_paths is None
        ):  # Both are None or both are provided
            raise ValueError(
                "You must specify exactly one of 'agents' or 'agent_paths'"
            )

        # if no callback is provided, disable streaming, hey don't have anywhere to go
        if message_callback is None and stream_tokens is True:
            raise ValueError("stream_tokens cannot be True if message_callback is None")
        # default to streaming if a callback is provided and no preference is given
        if stream_tokens is None and message_callback:
            stream_tokens = True

        # create noop callback if none is provided, keeps rest of the code cleaner
        if message_callback is None:

            async def noop_callback(*args, **kwargs):
                pass

            message_callback = noop_callback

        self.mm = ModelManager()
        self._message_callback = message_callback  # send messages back to the UI

        # Load agents
        self._agents = agents if agents is not None else {}
        self._agents = self._load_agents(agent_paths) if agent_paths else self._agents
        self._chooseable_agents = [
            agent_name
            for agent_name, val in self._agents.items()
            if val.get("chooseable", True)
        ]

        # streaming
        self._stream_tokens = stream_tokens  # streaming currently enabled or not
        self._streaming_preference = stream_tokens  # remember the last setting

        # model being used by the agent, will be set when a new conversation is started
        self._model_id = None

        # Will be used to cancel ongoing tasks
        self._cancelation_token = None

        # Inialize available tools
        if tools_directory is None:
            # Load only default tools or none at all
            self.tools = load_tools(None) if load_default_tools else {}
        else:
            # Load custom tools; optionally merge default tools (custom overrides defaults)
            custom_tools = load_tools(tools_directory)
            if load_default_tools:
                default_tools = load_tools(None)
                self.tools = {**default_tools, **custom_tools}
            else:
                self.tools = custom_tools

    def new_agent(
        self, agent_name, model_name, prompt, tools: list | None = None
    ) -> None:
        """Create a new agent with the given name, model, tools, and prompt"""
        pass

    @property
    def prompt(self) -> str:
        """Returns the current prompt"""
        # return self.agent.prompt
        return self._prompt

    @property
    def description(self) -> str:
        """Returns the current prompt"""
        # return self.agent.prompt
        return self._description

    @property
    def agents(self) -> dict:
        """Return the agent structure"""
        return self._agents

    @property
    def chooseable_agents(self) -> list:
        """Return list of agents the UI can choose from"""
        return self._chooseable_agents

    @property
    def model(self) -> str:
        """Returns the current model"""
        return self._model_id

    @property
    def stream_tokens(self) -> bool | None:
        """Are we currently streaming tokens if they are supported

        Returns:
        -------
        bool | None
            True if currently streaming tokens, False if not, None if not supported
        """

        return self._stream_tokens

    @stream_tokens.setter
    def stream_tokens(self, value: bool) -> None:
        """enable or disable token streaming"""

        if not isinstance(value, bool):
            raise ValueError("stream_tokens must be a boolean")

        # If currently disabled by logic, don't allow it to be enabled
        if self._stream_tokens is None:
            logger.info(
                f"token streaming disabled, setting stream_tokens to {value} ignored"
            )
            return

        # This remembers the last setting, so that if the model doesn't support
        # streaming, we know what to return to when switching to one that does
        self._streaming_preference = value
        self._stream_tokens = value
        self._set_agent_streaming()

    def _set_agent_streaming(self) -> None:
        """Reset the streaming callback for the agent"""

        value = self._stream_tokens

        if hasattr(self, "agent"):
            # HACK TODO - this needs to becone a public toggle
            self.agent._model_client_stream = value
            logger.info(f"token streaming for {self.agent.name} set to {value}")
        else:
            raise ValueError("stream_tokens can only be set if there is an agent")

    def cancel(self) -> None:
        """Cancel the current conversation"""
        if self._cancelation_token:
            self._cancelation_token.cancel()

    def terminate(self) -> None:
        """Terminate the current conversation"""
        if hasattr(self, "terminator"):
            self.terminator.set()

    def clear_memory(self) -> None:
        """Clear the agent's model context memory"""
        if hasattr(self, "agent") and hasattr(self.agent, "_model_context"):
            try:
                ctx = self.agent._model_context
                clear = getattr(ctx, "clear", None)
                if callable(clear):
                    clear()
            except Exception:
                logger.debug("Failed to clear model context", exc_info=True)

    async def update_memory(self, state: dict) -> None:
        await self.agent.load_state(state)

    async def get_memory(self) -> Mapping[str, Any]:
        """Returns the current memory in a recoverable text format"""
        return await self.agent.save_state()

    async def new_conversation(
        self,
        agent: str,
        model_id: str = None,
        temperature: float = None,
        stream_tokens: bool = True,
    ) -> None:
        """Intialize a new conversation with the given agent and model

        Parameters
        ----------
        agent : str
            agent to use
        model_id : str, optional
            model to use (overrides agent config/default)
        temperature : float, optional
            temperature to use (overrides agent config/default)
        stream_tokens: bool, optional
            if the model should stream tokens back to the UI
        """

        """
        Thoughts:  model_id and temperature will be for the agent that is interacting
        with the user.  For single-model agents, this will be the same as going straight
        to the model.

        For multi-agent teams, it will only affect the agent that is currently
        interacting with the user.  The other agents in the team will have their own
        model_id and temperature settings from the agent dictionary, or will use the
        default.
        """

        agent_data = self._agents[agent]

        # Use model from argument, agent config, or default
        if model_id is None:
            model_id = agent_data.get("model", self.mm.default_chat_model)
        # Use temperature from argument, agent config, or default
        if temperature is None:
            temperature = agent_data.get(
                "temperature", self.mm.default_chat_temperature
            )

        self._prompt = agent_data["prompt"] if "prompt" in agent_data else ""
        self._description = (
            agent_data["description"] if "description" in agent_data else ""
        )

        if "type" in agent_data and agent_data["type"] == "team":
            # Team-based Agents
            self.agent_team = self._create_team(agent_data["team_type"], agent_data)
            self.agent = self.agent_team._participants[0]

            # currently not streaming tokens for team agents
            self._stream_tokens = None
            logger.info("token streaming for team-based agents currently disabled")

        else:
            # Solo Agent
            self.model_client = self.mm.open_model(model_id)
            self._model_id = model_id

            # don't use tools if the model does't support them
            if (
                not self.mm.get_tool_support(model_id)
                or not self.model_client.model_info["function_calling"]
                or "tools" not in agent_data
            ):
                tools = None
            else:
                tools = [
                    self.tools[tool]
                    for tool in agent_data["tools"]
                    if tool in self.tools
                ]

            # Build the model_context
            model_context = UnboundedChatCompletionContext()

            # system message if supported
            if self.mm.get_system_prompt_support(model_id):
                system_message = self._prompt
            else:
                system_message = None
                await model_context.add_message(
                    UserMessage(content=self._prompt, source="user")
                )

            # Load Extra multi-shot messages if they exist
            if "extra_context" not in self._agents[agent]:
                self._agents[agent]["extra_context"] = []
            for extra in self._agents[agent]["extra_context"]:
                if extra[0] == "ai":
                    await model_context.add_message(
                        AssistantMessage(content=extra[1], source=agent)
                    )
                elif extra[0] == "human":
                    await model_context.add_message(
                        UserMessage(content=extra[1], source="user")
                    )
                elif extra[0] == "system":
                    raise ValueError(f"system message not implemented: {extra[0]}")
                else:
                    raise ValueError(f"Unknown extra context type {extra[0]}")

            # build the agent
            if "type" in agent_data and agent_data["type"] == "autogen-agent":
                if agent_data["name"] == "websurfer":
                    self.agent = MultimodalWebSurfer(
                        model_client=self.model_client,
                        name=agent,
                    )
                    # not streaming builtin autogen agents right now
                    logger.info(
                        f"token streaming agent:{agent} disabled or not supported"
                    )
                    self._stream_tokens = None

                else:
                    raise ValueError(f"Unknown autogen agent type for agent:{agent}")
            else:
                self.agent = AssistantAgent(
                    name=agent,
                    model_client=self.model_client,
                    tools=tools,
                    model_context=model_context,
                    system_message=system_message,
                    model_client_stream=True,
                    reflect_on_tool_use=True,
                )

                messages = await self.agent._model_context.get_messages()
                logger.trace(f"messages: {messages}")

            # Set streaming to the current preference (if supported)

            # disable streaming if not supported by the model, otherwse use preference
            if not self.mm.get_streaming_support(model_id):
                self._stream_tokens = None
                self._set_agent_streaming()
                logger.info(f"token streaming for model {model_id} not supported")
            else:
                self._stream_tokens = self._streaming_preference
                self._set_agent_streaming()

            # Build the termination conditions
            terminators = []
            terminators.append(
                StopMessageTermination(),
            )
            max_rounds = agent_data["max_rounds"] if "max_rounds" in agent_data else 5
            terminators.append(MaxMessageTermination(max_rounds))
            if "termination_message" in agent_data:
                terminators.append(
                    TextMentionTermination(agent_data["termination_message"])
                )
            self.terminator = ExternalTermination()  # for custom terminations
            terminators.append(self.terminator)

            # new - defaulting oneshot to false
            self.oneshot = (
                False if "oneshot" not in agent_data else agent_data["oneshot"]
            )

            # create the group chat

            # Smart terminator to reflect on the conversation if not complete
            terminators.append(
                SmartReflectorTermination(
                    model_client=self.mm.open_model(self.mm.default_memory_model),
                    oneshot=self.oneshot,
                    agent_name=agent,
                )
            )

            logger.debug("creating RR group chat")
            termination = reduce(lambda x, y: x | y, terminators)

            self.agent_team = RoundRobinGroupChat(
                participants=[self.agent],
                termination_condition=termination,
            )

    async def ask(self, task: str) -> TaskResult:
        self._cancelation_token = CancellationToken()

        try:
            result: TaskResult = await self._consume_agent_stream(
                agent_runner=self.agent_team.run_stream,
                oneshot=self.oneshot,
                task=task,
                cancellation_token=self._cancelation_token,
            )
        except Exception as e:
            logger.error(f"Error in agent stream: {e}")
            result = TaskResult(
                messages=[
                    TextMessage(  # ensure a sequence of TextMessage
                        source="System",
                        content=f"Error in agent stream: {e}",
                    )
                ],
                stop_reason="error",
            )
            await self._message_callback(
                "Error in response from AI, see debug", flush=True
            )

        self._cancelation_token = None
        if result.stop_reason.startswith("Exception occurred"):
            # notifiy the UI that an exception occurred
            logger.warning(
                f"Exception occurred talking to the AI: {result.stop_reason}"
            )
            await self._message_callback(
                "Error in response from AI, see debug", flush=True
            )
        logger.debug(f"Final result: {result.stop_reason}")
        await asyncio.sleep(0.1)  # Allow for autogen to cleanup/end the conversation
        return result

    def _load_agents(self, paths: list[str]) -> dict:
        """Read the agent definition files and load the agents, or parse agent
        definitions from strings"""
        agent_files = []
        agent_strings = []
        for path in paths:
            if isinstance(path, str):
                logger.debug(f"Loading agent from path: {path}")
                # Check if it's a directory
                if os.path.isdir(path):
                    logger.debug(f"Loading agents from directory: {path}")
                    for filename in os.listdir(path):
                        if filename.endswith(".json") or filename.endswith(".yaml"):
                            agent_files.append(os.path.join(path, filename))
                # Check if it's a file
                elif (
                    path.endswith(".json") or path.endswith(".yaml")
                ) and os.path.exists(path):
                    logger.debug(f"Loading agent from file: {path}")
                    agent_files.append(path)
                else:
                    logger.debug(f"Assuming {path} is a YAML or JSON string")
                    # Try to detect if it's a JSON string, otherwise assume YAML
                    s = path.strip()
                    if (s.startswith("{") and s.endswith("}")) or (
                        s.startswith("[") and s.endswith("]")
                    ):
                        agent_strings.append(("json", s))
                    else:
                        agent_strings.append(("yaml", s))
        agents = {}
        # Load from files
        for file in agent_files:
            extension = os.path.splitext(file)[1]
            with open(file, encoding="utf8") as f:
                logger.debug(f"Loading agent file {file}")
                try:
                    if extension == ".json":
                        file_agents = json.load(f)
                    elif extension == ".yaml":
                        file_agents = yaml.safe_load(f)
                except FileNotFoundError:
                    logger.error(f"Error: file {file} not found.")
                except yaml.YAMLError as e:
                    logger.error(f"Error parsing YAML file {file}: {e}")
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON file {file}: {e}")
                except Exception as e:
                    logger.exception(
                        f"An unexpected error occurred processing {file}: {e}"
                    )
                if not isinstance(file_agents, dict):
                    error_msg = (
                        f"Agent file {file} must contain a mapping of agents, "
                        f"got {type(file_agents)}"
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                agents.update(file_agents)
        # Load from strings
        for fmt, data in agent_strings:
            logger.debug(f"Loading agent from string ({fmt})")
            try:
                if fmt == "json":
                    file_agents = json.loads(data)
                elif fmt == "yaml":
                    file_agents = yaml.safe_load(data)
                if not isinstance(file_agents, dict):
                    error_msg = (
                        f"Agent string ({fmt}) must be a mapping of agents, "
                        f"got {type(file_agents)}"
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                agents.update(file_agents)
            except (ValueError, AttributeError) as e:
                error_msg = f"Error parsing agent string ({fmt}): {e}"
                logger.error(error_msg)
                raise ValueError(error_msg) from e

        # Validate agents
        for agent_name, agent_data in agents.items():
            if not isinstance(agent_data, dict):
                raise ValueError(
                    f"Agent '{agent_name}' must be a dict, got {type(agent_data)}"
                )
            if "type" not in agent_data:
                raise ValueError(f"Agent '{agent_name}' missing required 'type' field")
            # 'prompt' is not required for team agents
            if agent_data.get("type") == "agent" and "prompt" not in agent_data:
                raise ValueError(
                    f"Agent '{agent_name}' missing required 'prompt' field"
                )
            if "description" not in agent_data:
                raise ValueError(
                    f"Agent '{agent_name}' missing required 'description' field"
                )
            if "type" in agent_data and agent_data["type"] == "team":
                if "agents" not in agent_data or not isinstance(
                    agent_data["agents"], list
                ):
                    raise ValueError(
                        f"Team agent '{agent_name}' must have an 'agents' list"
                    )
        return agents

    def _create_team(
        self, team_type: str, agent_data: dict
    ) -> RoundRobinGroupChat | SelectorGroupChat | MagenticOneGroupChat:
        """Create a team of agents

        Parameters
        ----------
        team_type : str
            type of team to create
        agent_data : dict
            description of the agent team
        """

        # agent_data needs to be a team
        if "type" not in agent_data or agent_data["type"] != "team":
            raise ValueError("agent_data 'type' for team must be 'team'")

        # build the agents
        agents = []
        for agent in agent_data["agents"]:
            subagent_data = self._agents[agent]
            if "model" not in subagent_data:
                subagent_data["model"] = self.mm.default_chat_model
            model_client = self.mm.open_model(subagent_data["model"])

            if "type" in subagent_data and subagent_data["type"] == "autogen-agent":
                if subagent_data["name"] == "websurfer":
                    agents.append(
                        MultimodalWebSurfer(
                            model_client=model_client,
                            name=agent,
                        )
                    )
                else:
                    raise ValueError(f"Unknown autogen agent type for agent:{agent}")
            else:
                # don't use tools if the model does't support them
                if (
                    not self.mm.get_tool_support(subagent_data["model"])
                    or not model_client.model_info["function_calling"]
                    or "tools" not in subagent_data
                ):
                    tools = None
                else:
                    # load the tools (skip unknown tool ids gracefully)
                    tools = []
                    for tool in subagent_data["tools"]:
                        if tool in self.tools:
                            tools.append(self.tools[tool])
                        else:
                            logger.warning(f"Tool {tool} not found; skipping.")

                agents.append(
                    AssistantAgent(
                        name=agent,
                        model_client=model_client,
                        tools=tools,
                        system_message=subagent_data["prompt"],
                        description=subagent_data["description"],
                        reflect_on_tool_use=True,
                    )
                )

        # constuct the team
        terminators = []
        max_rounds = agent_data["max_rounds"] if "max_rounds" in agent_data else 5
        terminators.append(MaxMessageTermination(max_rounds))
        if "termination_message" in agent_data:
            terminators.append(
                TextMentionTermination(agent_data["termination_message"])
            )
        self.terminator = ExternalTermination()  # for custom terminations
        terminators.append(self.terminator)
        termination = reduce(lambda x, y: x | y, terminators)

        if "oneshot" in agent_data:
            self.oneshot = agent_data["oneshot"]
        else:
            self.oneshot = True if len(agents) == 1 else False

        if team_type == "round_robin":
            return RoundRobinGroupChat(agents, termination_condition=termination)
        elif team_type == "selector":
            if "team_model" not in agent_data:
                team_model = self.mm.open_model(self.mm.default_chat_model)
            else:
                team_model = self.mm.open_model(agent_data["team_model"])
            allow_repeated_speaker = agent_data.get("allow_repeated_speaker", False)

            if "selector_prompt" in agent_data:
                return SelectorGroupChat(
                    agents,
                    model_client=team_model,
                    selector_prompt=agent_data["selector_prompt"],
                    termination_condition=termination,
                    allow_repeated_speaker=allow_repeated_speaker,
                )
            else:
                return SelectorGroupChat(
                    agents,
                    model_client=team_model,
                    allow_repeated_speaker=allow_repeated_speaker,
                    termination_condition=termination,
                )
        elif team_type == "magnetic_one":
            if "team_model" not in agent_data:
                team_model = self.mm.open_model(self.mm.default_chat_model)
            else:
                team_model = self.mm.open_model(agent_data["team_model"])
            return MagenticOneGroupChat(
                agents, model_client=team_model, termination_condition=termination
            )
        else:
            raise ValueError(f"Unknown team type {team_type}")

    async def _consume_agent_stream(
        self,
        agent_runner: Callable[..., AsyncIterable],  # type of run_stream
        oneshot: bool,
        task: str,
        cancellation_token: CancellationToken,
    ) -> TaskResult:
        """Run the agent team in streaming mode, handle responses, and return
        final TaskResult."""
        try:
            async for response in agent_runner(
                task=task, cancellation_token=cancellation_token
            ):
                # Dispatch to correct handler
                if response is None:
                    logger.debug("Ignoring None response")
                    continue

                if isinstance(response, ModelClientStreamingChunkEvent):
                    await self._handle_stream_chunk(response)
                    continue

                if isinstance(response, MultiModalMessage):
                    await self._handle_multi_modal(response)
                    continue

                if isinstance(response, StopMessage):
                    logger.debug(f"Received StopMessage: {response.content}")
                    return TaskResult(
                        messages=[
                            TextMessage(  # ensure a sequence of TextMessage
                                source="System",
                                content="Presumed done",
                            )
                        ],
                        stop_reason="presumed done",
                    )

                if isinstance(response, TaskResult):
                    return response

                if isinstance(response, TextMessage):
                    handled = await self._handle_text_message(response, oneshot=oneshot)
                    if handled:
                        return handled
                    continue

                if isinstance(response, ThoughtEvent):
                    await self._handle_thought_event(response)
                    continue

                if isinstance(response, ToolCallExecutionEvent):
                    await self._handle_tool_call_execution(response)
                    continue

                if isinstance(response, ToolCallRequestEvent):
                    await self._handle_tool_call_request(response)
                    continue

                if isinstance(response, ToolCallSummaryMessage):
                    await self._handle_tool_summary(response)
                    continue

                if isinstance(response, UserInputRequestedEvent):
                    await self._handle_user_input_request(response)
                    continue

                # Unknown event
                logger.warning(f"Received unknown response type: {response!r}")
                await self._message_callback("<unknown>", flush=True)
                await self._message_callback(repr(response), flush=True)

            # TODO: This is a placeholder for when the stream ends without a TaskResult
            logger.error("Stream ended without a TaskResult")
            return TaskResult(
                messages=[TextMessage(source="System", content="End of stream")],
                stop_reason="end_of_stream",
            )
        except Exception as e:
            logger.error(f"Error in agent stream: {e}")
            await self._message_callback("Error in responses, see debug", flush=True)
            return TaskResult(
                messages=[
                    TextMessage(source="System", content=f"Error in agent stream: {e}")
                ],
                stop_reason="error",
            )

    # - - Handlers for different response types

    async def _handle_multi_modal(self, response: MultiModalMessage) -> None:
        await self._message_callback(
            f"MM:{response.content}", agent=response.source, complete=True
        )

    async def _handle_stream_chunk(
        self, response: ModelClientStreamingChunkEvent
    ) -> None:
        await self._message_callback(
            response.content, agent=response.source, complete=False
        )

    async def _handle_text_message(
        self, response: TextMessage, oneshot: bool
    ) -> TaskResult | None:
        if response.source == "user":
            # This is presumably just an echo of the user’s prompt
            return

        logger.trace(f"TextMessage from {response.source}: {response.content}")

        # only show the message if we're not streaming, otherwise the streaming
        # will handle it
        if not self._stream_tokens:
            await self._message_callback(
                response.content, agent=response.source, complete=True
            )

    async def _handle_thought_event(self, response: ThoughtEvent) -> None:
        logger.debug(f"ThoughtEvent: {response.content}")
        await self._message_callback(
            f"\n\n*(Thinking: {response.content})*\n\n",
            agent=response.source,
            complete=False,
        )

    async def _handle_tool_summary(self, response: ToolCallSummaryMessage) -> None:
        logger.debug(f"Ignoring tool call summary message: {response.content}")

    async def _handle_tool_call_execution(
        self, response: ToolCallExecutionEvent
    ) -> None:
        logger.info(f"Tool call result: {response.content}")
        await self._message_callback("done", agent=response.source, complete=True)

    async def _handle_tool_call_request(self, response: ToolCallRequestEvent) -> None:
        tool_message = "\n\ncalling tool"
        for tool in response.content:
            tool_message += f"{tool.name} with arguments:\n{tool.arguments}\n"
        tool_message += "..."
        await self._message_callback(tool_message, agent=response.source)

    async def _handle_user_input_request(
        self, response: UserInputRequestedEvent
    ) -> None:
        logger.info(f"UserInputRequestedEvent: {response.content}")
        await self._message_callback(
            response.content, agent=response.source, complete=True
        )


class AgentManager(AutogenManager):
    """Alias for AutogenManager"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LLMTools:
    llmtools_mm = ModelManager()
    llmtools_summary_model: (
        AzureOpenAIChatCompletionClient | OpenAIChatCompletionClient
    ) = llmtools_mm.open_model(llmtools_mm.default_memory_model)

    def __init__(self):
        """Builds the intent prompt template"""
        pass

    @staticmethod
    async def aget_summary_label(conversation: str) -> str:
        """Returns the a very short summary of a conversation suitable for a label"""
        system_message = label_prompt.format(conversation=conversation)
        try:
            out = await LLMTools.llmtools_summary_model.create(
                [SystemMessage(content=system_message)]
            )
        except Exception as e:
            logger.error(f"Error getting summary label: {type(e)}:{e}")
            raise
        return out.content

    @staticmethod
    async def get_conversation_summary(conversation: str) -> str:
        """Returns the summary of a conversation"""
        system_message = summary_prompt.format(conversation=conversation)
        try:
            out = await LLMTools.llmtools_summary_model.create(
                [SystemMessage(content=system_message)]
            )
        except Exception as e:
            logger.error(f"Error getting conversation summary: {type(e)}:{e}")
            raise
        return out.content
