from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Type,
    Union,
    cast,
    overload,
)

from pydantic import BaseModel

from planar.ai.agent_utils import (
    AgentEventEmitter,
    AgentEventType,
    ToolCallResult,
    create_tool_definition,
    extract_files_from_model,
    get_agent_config,
    render_template,
)
from planar.ai.models import (
    AgentConfig,
    AgentRunResult,
    AssistantMessage,
    CompletionResponse,
    ModelMessage,
    SystemMessage,
    ToolResponse,
    UserMessage,
)
from planar.ai.providers import Anthropic, Gemini, Model, OpenAI
from planar.logging import get_logger
from planar.modeling.field_helpers import JsonSchema
from planar.utils import P, R, T, U, utc_now
from planar.workflows import as_step
from planar.workflows.models import StepType

logger = get_logger(__name__)


def _parse_model_string(model_str: str) -> Model:
    """Parse a model string (e.g., 'openai:gpt-4.1') into a Model instance."""
    parts = model_str.split(":", 1)
    if len(parts) != 2:
        raise ValueError(
            f"Invalid model format: {model_str}. Expected format: 'provider:model_id'"
        )

    provider_id, model_id = parts

    if provider_id.lower() == "openai":
        return OpenAI.model(model_id)
    elif provider_id.lower() == "anthropic":
        return Anthropic.model(model_id)
    elif provider_id.lower() == "gemini":
        return Gemini.model(model_id)
    else:
        raise ValueError(f"Unsupported provider: {provider_id}")


@dataclass
class AgentBase[
    # TODO: add `= str` default when we upgrade to 3.13
    TInput: BaseModel | str,
    TOutput: BaseModel | str,
](abc.ABC):
    """An LLM-powered agent that can be called directly within workflows."""

    name: str
    system_prompt: str
    output_type: Type[TOutput] | None = None
    input_type: Type[TInput] | None = None
    user_prompt: str = ""
    tools: List[Callable] = field(default_factory=list)
    max_turns: int = 2
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    event_emitter: AgentEventEmitter | None = None
    durable: bool = True

    # TODO: move here to serialize to frontend
    #
    # built_in_vars: Dict[str, str] = field(default_factory=lambda: {
    #     "datetime_now": datetime.datetime.now().isoformat(),
    #     "date_today": datetime.date.today().isoformat(),
    # })

    def __post_init__(self):
        if self.input_type:
            if (
                not issubclass(self.input_type, BaseModel)
                and self.input_type is not str
            ):
                raise ValueError(
                    "input_type must be 'str' or a subclass of a Pydantic model"
                )
        if self.max_turns < 1:
            raise ValueError("Max_turns must be greater than or equal to 1.")
        if self.tools and self.max_turns <= 1:
            raise ValueError(
                "For tool calling to work, max_turns must be greater than 1."
            )

    def input_schema(self) -> JsonSchema | None:
        if self.input_type is None:
            return None
        if self.input_type is str:
            return None
        assert issubclass(self.input_type, BaseModel), (
            "input_type must be a subclass of BaseModel or str"
        )
        return self.input_type.model_json_schema()

    def output_schema(self) -> JsonSchema | None:
        if self.output_type is None:
            return None
        if self.output_type is str:
            return None
        assert issubclass(self.output_type, BaseModel), (
            "output_type must be a subclass of BaseModel or str"
        )
        return self.output_type.model_json_schema()

    @overload
    async def __call__(
        self: "AgentBase[TInput, str]",
        input_value: TInput,
    ) -> AgentRunResult[str]: ...

    @overload
    async def __call__(
        self: "AgentBase[TInput, TOutput]",
        input_value: TInput,
    ) -> AgentRunResult[TOutput]: ...

    def as_step_if_durable(
        self,
        func: Callable[P, Coroutine[T, U, R]],
        step_type: StepType,
        display_name: str | None = None,
        return_type: Type[R] | None = None,
    ) -> Callable[P, Coroutine[T, U, R]]:
        if not self.durable:
            return func
        return as_step(
            func,
            step_type=step_type,
            display_name=display_name or self.name,
            return_type=return_type,
        )

    async def __call__(
        self,
        input_value: TInput,
    ) -> AgentRunResult[Any]:
        if self.input_type is not None and not isinstance(input_value, self.input_type):
            raise ValueError(
                f"Input value must be of type {self.input_type}, but got {type(input_value)}"
            )
        elif not isinstance(input_value, (str, BaseModel)):
            # Should not happen based on type constraints, but just in case
            # user does not have type checking enabled
            raise ValueError(
                "Input value must be a string or a Pydantic model if input_type is not provided"
            )

        if self.output_type is None:
            run_step = self.as_step_if_durable(
                self.run_step,
                step_type=StepType.AGENT,
                display_name=self.name,
                return_type=AgentRunResult[str],
            )
        else:
            run_step = self.as_step_if_durable(
                self.run_step,
                step_type=StepType.AGENT,
                display_name=self.name,
                return_type=AgentRunResult[self.output_type],
            )

        result = await run_step(input_value=input_value)
        # Cast the result to ensure type compatibility
        return cast(AgentRunResult[TOutput], result)

    @abc.abstractmethod
    async def run_step(
        self,
        input_value: TInput,
    ) -> AgentRunResult[TOutput]: ...

    @abc.abstractmethod
    def get_model_str(self) -> str: ...

    def to_config(self) -> AgentConfig:
        return AgentConfig(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
            model=self.get_model_str(),
            max_turns=self.max_turns,
            model_parameters=self.model_parameters,
        )


@dataclass
class Agent[
    TInput: BaseModel | str,
    TOutput: BaseModel | str,
](AgentBase[TInput, TOutput]):
    model: Union[str, Model] = "openai:gpt-4.1"

    async def run_step(
        self,
        input_value: TInput,
    ) -> AgentRunResult[TOutput]:
        """Execute the agent with the provided inputs.

        Args:
            input_value: The primary input value to the agent, can be a string or Pydantic model
            **kwargs: Alternative way to pass inputs as keyword arguments

        Returns:
            AgentRunResult containing the agent's response
        """
        event_emitter = self.event_emitter
        logger.debug(
            "agent run_step called",
            agent_name=self.name,
            input_type=type(input_value),
            config=self.to_config(),
        )
        result = None

        config = await get_agent_config(self.name, self.to_config())
        logger.debug("agent using config", agent_name=self.name, config=config)

        input_map: dict[str, str | dict[str, Any]] = {}

        files = extract_files_from_model(input_value)
        logger.debug(
            "extracted files from input for agent",
            num_files=len(files),
            agent_name=self.name,
        )
        match input_value:
            case BaseModel():
                if self.input_type and not isinstance(input_value, self.input_type):
                    logger.warning(
                        "input value type mismatch for agent",
                        agent_name=self.name,
                        expected_type=self.input_type,
                        got_type=type(input_value),
                    )
                    raise ValueError(
                        f"Input value must be of type {self.input_type}, but got {type(input_value)}"
                    )
                input_map["input"] = cast(BaseModel, input_value).model_dump()
            case str():
                input_map["input"] = input_value
            case _:
                logger.warning(
                    "unexpected input value type for agent",
                    agent_name=self.name,
                    type=type(input_value),
                )
                raise ValueError(f"Unexpected input value type: {type(input_value)}")

        # Add built-in variables
        # TODO: Make deterministic or step
        built_in_vars = {
            "datetime_now": utc_now().isoformat(),
            "date_today": utc_now().date().isoformat(),
        }
        input_map.update(built_in_vars)

        # Format the prompts with the provided arguments using Jinja templates
        try:
            formatted_system_prompt = (
                render_template(config.system_prompt, input_map)
                if config.system_prompt
                else ""
            )
            formatted_user_prompt = (
                render_template(config.user_prompt, input_map)
                if config.user_prompt
                else ""
            )
        except ValueError as e:
            logger.exception("error formatting prompts for agent", agent_name=self.name)
            raise ValueError(f"Missing required parameter for prompt formatting: {e}")

        # Get the LLM provider and model
        model_config = config.model
        if isinstance(model_config, str):
            model = _parse_model_string(model_config)
        else:
            model = model_config

        # Apply model parameters if specified
        if config.model_parameters:
            model = model.with_parameters(**config.model_parameters)

        # Prepare structured messages
        messages: List[ModelMessage] = []
        if formatted_system_prompt:
            messages.append(SystemMessage(content=formatted_system_prompt))

        if formatted_user_prompt:
            messages.append(UserMessage(content=formatted_user_prompt, files=files))

        # Prepare tools if provided
        tool_definitions = None
        if self.tools:
            tool_definitions = [create_tool_definition(tool) for tool in self.tools]

        # Determine output type for the provider call
        # Pass the Pydantic model type if output_type is a subclass of BaseModel,
        # otherwise pass None (indicating string output is expected).
        output_type_for_provider: Type[BaseModel] | None = None
        # Use issubclass safely by checking if output_type is a type first
        if inspect.isclass(self.output_type) and issubclass(
            self.output_type, BaseModel
        ):
            output_type_for_provider = cast(Type[BaseModel], self.output_type)

        # Execute the LLM call
        max_turns = config.max_turns

        # Single turn completion (default case)
        result = None
        if not tool_definitions:
            logger.debug(
                "agent performing single turn completion",
                agent_name=self.name,
                model=model.model_spec,
                output_type=output_type_for_provider,
            )
            response = await self.as_step_if_durable(
                model.provider_class.complete,
                step_type=StepType.AGENT,
                return_type=CompletionResponse[output_type_for_provider or str],
            )(
                model_spec=model.model_spec,
                messages=messages,
                output_type=output_type_for_provider,
            )
            result = response.content

            # Emit response event if event_emitter is provided
            if event_emitter:
                event_emitter.emit(AgentEventType.RESPONSE, response.content)
        else:
            logger.debug(
                "agent performing multi-turn completion with tools",
                agent_name=self.name,
                max_turns=max_turns,
            )
            # Multi-turn with tools
            turns_left = max_turns
            while turns_left > 0:
                turns_left -= 1
                logger.debug("agent turn", agent_name=self.name, turns_left=turns_left)

                # Get model response
                response = await self.as_step_if_durable(
                    model.provider_class.complete,
                    step_type=StepType.AGENT,
                    return_type=CompletionResponse[output_type_for_provider or str],
                )(
                    model_spec=model.model_spec,
                    messages=messages,
                    output_type=output_type_for_provider,
                    tools=tool_definitions,
                )

                # Emit response event if event_emitter is provided
                if event_emitter:
                    event_emitter.emit(AgentEventType.RESPONSE, response.content)

                # If no tool calls or last turn, return content
                if not response.tool_calls or turns_left == 0:
                    logger.debug(
                        "agent completion: no tool calls or last turn",
                        agent_name=self.name,
                        has_content=response.content is not None,
                    )
                    result = response.content
                    break

                # Process tool calls
                logger.debug(
                    "agent received tool calls",
                    agent_name=self.name,
                    num_tool_calls=len(response.tool_calls),
                )
                assistant_message = AssistantMessage(
                    content=None,
                    tool_calls=response.tool_calls,
                )
                messages.append(assistant_message)

                # Execute each tool and add tool responses to messages
                for tool_call_idx, tool_call in enumerate(response.tool_calls):
                    logger.debug(
                        "agent processing tool call",
                        agent_name=self.name,
                        tool_call_index=tool_call_idx + 1,
                        tool_call_id=tool_call.id,
                        tool_call_name=tool_call.name,
                    )
                    # Find the matching tool function
                    tool_fn = next(
                        (t for t in self.tools if t.__name__ == tool_call.name),
                        None,
                    )

                    if not tool_fn:
                        tool_result = f"Error: Tool '{tool_call.name}' not found."
                        logger.warning(
                            "tool not found for agent",
                            tool_name=tool_call.name,
                            agent_name=self.name,
                        )
                    else:
                        # Execute the tool with the provided arguments
                        tool_result = await self.as_step_if_durable(
                            tool_fn,
                            step_type=StepType.TOOL_CALL,
                        )(**tool_call.arguments)
                        logger.info(
                            "tool executed by agent",
                            tool_name=tool_call.name,
                            agent_name=self.name,
                            result_type=type(tool_result),
                        )

                    # Create a tool response
                    tool_response = ToolResponse(
                        tool_call_id=tool_call.id or "call_1", content=str(tool_result)
                    )

                    # Emit tool response event if event_emitter is provided
                    if event_emitter:
                        event_emitter.emit(
                            AgentEventType.TOOL_RESPONSE,
                            ToolCallResult(
                                tool_call_id=tool_call.id or "call_1",
                                tool_call_name=tool_call.name,
                                content=tool_result,
                            ),
                        )

                    # Convert the tool response to a message based on provider
                    tool_message = model.provider_class.format_tool_response(
                        tool_response
                    )
                    messages.append(tool_message)

                # Continue to next turn

            if result is None:
                logger.warning(
                    "agent completed tool interactions but result is none",
                    agent_name=self.name,
                    expected_type=self.output_type,
                )
                raise ValueError(
                    f"Reached max turns without the expected result of type {self.output_type}. "
                    "You may need to increase the max_turns parameter or update the Agent instructions."
                )

        if event_emitter:
            event_emitter.emit(AgentEventType.COMPLETED, result)

        if result is None:
            logger.warning("agent final result is none", agent_name=self.name)
            raise ValueError("No result obtained after tool interactions")

        logger.info(
            "agent completed",
            agent_name=self.name,
            final_result_type=type(result),
        )
        return AgentRunResult[TOutput](output=cast(TOutput, result))

    def get_model_str(self) -> str:
        return str(self.model)
