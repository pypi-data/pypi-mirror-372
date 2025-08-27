"""
Provider module for AI model integrations.
"""

import base64
import json
import re
from abc import ABC, abstractmethod
from typing import Any, Literal, Type, TypeAlias

# TODO: Make provider imports lazy based on providers instealled
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_ai import messages as pydantic_ai
from pydantic_ai._output import OutputObjectDefinition
from pydantic_ai.direct import model_request as pydantic_ai_model_request
from pydantic_ai.models import (
    ModelRequestParameters as PydanticAIModelRequestParameters,
)
from pydantic_ai.tools import ToolDefinition as PydanticAIToolDefinition

from planar.logging import get_logger
from planar.session import get_config

from .models import (
    AssistantMessage,
    Base64Content,
    CompletionResponse,
    FileContent,
    FileIdContent,
    FileMap,
    ModelMessage,
    SystemMessage,
    T,
    ToolCall,
    ToolDefinition,
    ToolMessage,
    ToolResponse,
    UserMessage,
)

logger = get_logger(__name__)

AnthropicKwargs: TypeAlias = dict[Literal["api_key", "base_url"], str]


class ModelSpec(BaseModel):
    """Pydantic model for AI model specifications."""

    model_id: str
    parameters: dict[str, Any] = {}


class Model:
    """Base class for AI model specifications."""

    provider_class: Type["Provider"]  # set by subclasses
    name: str

    def __init__(self, model_id: str):
        self.model_spec = ModelSpec(model_id=model_id)

    def with_parameters(self, **kwargs) -> "Model":
        updated_params = self.model_spec.parameters.copy()
        updated_params.update(kwargs)
        new_instance = self.__class__(self.model_spec.model_id)
        new_instance.model_spec.parameters = updated_params
        return new_instance

    def __str__(self) -> str:
        return f"{self.name}:{self.model_spec.model_id}"

    def __repr__(self) -> str:
        return self.__str__()


class Provider(ABC):
    """Base class for AI model providers with tool support."""

    @staticmethod
    @abstractmethod
    async def complete(
        model_spec: ModelSpec,
        messages: list[ModelMessage],
        output_type: Type[T] | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> CompletionResponse[T | str]:
        """
        Generate a completion, potentially using tools.

        Args:
            model_spec: The model specification to use.
            messages: List of structured messages for the model.
            output_type: Optional desired output type (Pydantic model) for structured output.
            tools: Optional list of tools the model can use.

        Returns:
            CompletionResponse containing either content or tool calls.
        """
        pass

    @staticmethod
    @abstractmethod
    def model(model_id: str) -> Model:
        """Create a model instance for a custom model ID."""
        pass

    @staticmethod
    @abstractmethod
    def format_tool_response(tool_response: ToolResponse) -> ToolMessage:
        """Format a tool response into a message for the provider.

        Args:
            tool_response: The tool response to format.

        Returns:
            A formatted tool message for the provider.
        """
        raise NotImplementedError("Subclasses must implement format_tool_response")

    @staticmethod
    @abstractmethod
    def prepare_messages(
        messages: list[ModelMessage], file_map: FileMap
    ) -> list[dict[str, Any]]:
        """Prepare messages from Planar representations into the format expected by the provider, including file upload or conversion.

        Args:
            messages: List of structured messages.

        Returns:
            List of messages in the format expected by the provider.
        """
        raise NotImplementedError("Subclasses must implement prepare_messages")


class OpenAIProvider(Provider):
    """OpenAI provider implementation."""

    @staticmethod
    def format_tool_response(tool_response: ToolResponse) -> ToolMessage:
        """Format a tool response into a message for OpenAI.

        Args:
            tool_response: The tool response to format.

        Returns:
            A formatted tool message.
        """
        return ToolMessage(
            content=tool_response.content,
            tool_call_id=tool_response.tool_call_id or "call_1",
        )

    @staticmethod
    def prepare_messages(
        messages: list[ModelMessage], file_map: FileMap | None = None
    ) -> list[dict[str, Any]]:
        """Prepare messages from Planar representations into the format expected by the provider, including file upload or conversion.

        Args:
            messages: List of structured messages.

        Returns:
            List of messages in OpenAI format.
        """

        formatted_messages = []

        for message in messages:
            if isinstance(message, SystemMessage):
                formatted_messages.append(
                    {"role": "system", "content": message.content}
                )
            elif isinstance(message, UserMessage):
                content = []
                files: list[FileContent] = []
                if message.files:
                    if not file_map:
                        raise ValueError("File map empty while user message has files.")
                    for file in message.files:
                        if str(file.id) not in file_map.mapping:
                            raise ValueError(
                                f"File {file} not found in file map {file_map}."
                            )
                        files.append(file_map.mapping[str(file.id)])

                if files:
                    for file in files:
                        match file:
                            case Base64Content():
                                content.extend(
                                    [
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:{file.content_type};base64,{file.content}",
                                            },
                                        }
                                    ]
                                )
                            case FileIdContent():
                                content.extend(
                                    [
                                        {
                                            "type": "file",
                                            "file": {"file_id": file.content},
                                        }
                                    ]
                                )
                            case _:
                                raise ValueError(f"Unsupported file type: {type(file)}")

                content.append({"type": "text", "text": message.content})
                formatted_messages.append({"role": "user", "content": content})
            elif isinstance(message, ToolMessage):
                formatted_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": message.tool_call_id,
                        "content": message.content,
                    }
                )
            elif isinstance(message, AssistantMessage):
                if message.tool_calls:
                    assistant_msg = {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [],
                    }

                    for tool_call in message.tool_calls:
                        formatted_tool_call = {
                            "id": tool_call.id
                            or f"call_{len(assistant_msg['tool_calls']) + 1}",
                            "type": "function",
                            "function": {
                                "name": tool_call.name,
                                "arguments": json.dumps(tool_call.arguments),
                            },
                        }
                        assistant_msg["tool_calls"].append(formatted_tool_call)

                    formatted_messages.append(assistant_msg)
                else:
                    formatted_messages.append(
                        {"role": "assistant", "content": message.content}
                    )

        return formatted_messages

    @staticmethod
    async def _build_file_map(
        client: AsyncOpenAI, messages: list[ModelMessage]
    ) -> FileMap:
        logger.debug("building file map", num_messages=len(messages))
        file_dict = {}
        for message_idx, message in enumerate(messages):
            if isinstance(message, UserMessage) and message.files:
                logger.debug(
                    "processing files in message",
                    num_files=len(message.files),
                    message_index=message_idx,
                )
                for file_idx, file in enumerate(message.files):
                    logger.debug(
                        "processing file",
                        file_index=file_idx,
                        file_id=file.id,
                        content_type=file.content_type,
                    )
                    match file.content_type:
                        case "application/pdf":
                            logger.debug(
                                "uploading pdf file to openai", filename=file.filename
                            )
                            # upload the file to the provider
                            openai_file = await client.files.create(
                                file=(
                                    file.filename,
                                    await file.get_content(),
                                    file.content_type,
                                ),
                                purpose="user_data",
                            )
                            logger.info(
                                "uploaded pdf file to openai",
                                filename=file.filename,
                                openai_file_id=openai_file.id,
                            )
                            file_dict[str(file.id)] = FileIdContent(
                                content=openai_file.id
                            )
                        case "image/png" | "image/jpeg" | "image/gif" | "image/webp":
                            logger.debug(
                                "encoding image file to base64", filename=file.filename
                            )
                            file_dict[str(file.id)] = Base64Content(
                                content=base64.b64encode(
                                    await file.get_content()
                                ).decode("utf-8"),
                                content_type=file.content_type,
                            )
                        case _:
                            logger.warning(
                                "unsupported file type for openai",
                                content_type=file.content_type,
                            )
                            raise ValueError(
                                f"Unsupported file type: {file.content_type}"
                            )
        logger.debug("file map built", num_entries=len(file_dict))
        return FileMap(mapping=file_dict)

    @staticmethod
    async def complete(
        model_spec: ModelSpec,
        messages: list[ModelMessage],
        output_type: Type[T] | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> CompletionResponse[T | str]:
        """
        Generate a completion using OpenAI.

        Args:
            model_spec: The model specification to use.
            messages: List of structured messages.
            output_type: Optional desired output type (Pydantic model) for structured output.
            tools: Optional list of tools the model can use.

        Returns:
            CompletionResponse containing either content or tool calls.
        """
        logger.debug(
            "openaiprovider.complete called",
            model_spec=model_spec,
            output_type=output_type,
            has_tools=tools is not None,
        )
        try:
            from openai import AsyncOpenAI  # noqa: PLC0415
        except ImportError as e:
            logger.exception("openai package not installed")
            raise ImportError(
                "OpenAI package is not installed. Install it with 'pip install openai'"
            ) from e

        try:
            # Get config from context
            config = get_config()

            # Check if OpenAI config is available
            if not config or not config.ai_providers or not config.ai_providers.openai:
                logger.warning("openai configuration is missing in planarconfig")
                raise ValueError(
                    "OpenAI configuration is missing. Please provide OpenAI credentials in your config."
                )

            openai_config = config.ai_providers.openai
            logger.debug("openai client configured from planarconfig")
            client = AsyncOpenAI(
                api_key=openai_config.api_key.get_secret_value(),
                base_url=openai_config.base_url,
                organization=openai_config.organization,
            )
        except (RuntimeError, ValueError) as e:
            # Fallback to environment variables when running outside of HTTP context
            # or when configuration is incomplete
            # client = AsyncOpenAI()  # Uses OPENAI_API_KEY from environment
            logger.exception(
                "failed to configure openai client from planarconfig or context"
            )
            raise ValueError("OpenAI configuration is missing.") from e

        file_map = await OpenAIProvider._build_file_map(client, messages)

        formatted_messages = OpenAIProvider.prepare_messages(messages, file_map)

        # TODO: Properly validate parameters
        kwargs = {
            "model": model_spec.model_id,
            "messages": formatted_messages,
            **model_spec.parameters,
        }

        # Handle function calling via tools
        if tools:
            formatted_tools = []
            for tool in tools:
                # Convert our Pydantic model to OpenAI's expected format
                schema = tool.parameters
                openai_params = {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                    "additionalProperties": False,
                }

                formatted_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": openai_params,
                            "strict": True,
                        },
                    }
                )
            kwargs["tools"] = formatted_tools

        # Handle structured output if output_type is provided
        completion = None
        if output_type is not None:
            if not issubclass(output_type, BaseModel):
                raise ValueError("Non-Pydantic structured output not supported yet.")

            # Verify name conforms to regex, otherwise OpenAI will throw an error
            if not re.match(r"^[a-zA-Z0-9_-]+$", output_type.__name__):
                output_type.__name__ = re.sub(
                    r"[^a-zA-Z0-9_-]", "_", output_type.__name__
                )

            completion = await client.beta.chat.completions.parse(
                response_format=output_type, **kwargs
            )
            logger.debug(
                "called openai beta.chat.completions.parse for structured output"
            )
        else:
            # Make the API call
            completion = await client.chat.completions.create(**kwargs)
            logger.debug("called openai chat.completions.create for standard output")

        assert completion
        # Process the response
        choice = completion.choices[0]
        logger.debug("openai completion choice", choice=choice)

        # Check for tool calls
        if choice.message.tool_calls:
            logger.debug(
                "openai response contains tool calls",
                num_tool_calls=len(choice.message.tool_calls),
            )
            tool_calls = []
            for tool_call_idx, tool_call in enumerate(choice.message.tool_calls):
                # Parse the function arguments from JSON string
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    logger.exception(
                        "failed to parse json arguments for tool call",
                        tool_name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                    )
                    arguments = {"raw_arguments": tool_call.function.arguments}

                tool_calls.append(
                    ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=arguments,
                    )
                )

            return CompletionResponse(content=None, tool_calls=tool_calls)

        # Process regular content
        content = choice.message.content

        # Parse JSON content if needed
        if output_type and issubclass(output_type, BaseModel) and content:
            try:
                if isinstance(content, str):
                    parsed_content = json.loads(content)
                    content = output_type.model_validate(parsed_content)
            except Exception:
                # If parsing fails, return the raw content
                logger.exception(
                    "failed to parse/validate structured output content",
                    content=content,
                )
                pass
        logger.debug("openai completion successful", content_type=type(content))
        return CompletionResponse(content=content, tool_calls=None)


class OpenAIModel(Model):
    """OpenAI-specific model implementation."""

    provider_class = OpenAIProvider
    name = "OpenAI"

    def __init__(self, model_id: str):
        super().__init__(model_id)


class OpenAI:
    # builder of OpenAI models
    @staticmethod
    def model(model_id: str) -> OpenAIModel:
        """Create a model instance for a custom OpenAI model ID."""
        return OpenAIModel(model_id)

    # OpenAI models using the model method
    gpt_4o = model("gpt-4o")
    gpt_4_1 = model("gpt-4.1")
    gpt_4_turbo = model("gpt-4-turbo")


class AnthropicProvider(Provider):
    """Anthropic provider implementation."""

    @staticmethod
    def model(model_id: str) -> "AnthropicModel":
        """Create a model instance for a custom Anthropic model ID."""
        return AnthropicModel(model_id)

    @staticmethod
    def format_tool_response(tool_response: ToolResponse) -> ToolMessage:
        """Format a tool response into a message for Anthropic.

        Args:
            tool_response: The tool response to format.

        Returns:
            A formatted tool message.
        """
        return ToolMessage(
            content=tool_response.content,
            tool_call_id=tool_response.tool_call_id or "call_1",
        )

    @staticmethod
    def prepare_messages(
        messages: list[ModelMessage], file_map: FileMap | None = None
    ) -> list[dict[str, Any]]:
        """Prepare messages from Planar representations into the format expected by the provider, including file upload or conversion.

        Args:
            messages: List of structured messages.

        Returns:
            List of messages in Anthropic format.
        """
        formatted_messages = []

        for message in messages:
            if isinstance(message, SystemMessage):
                formatted_messages.append(
                    {"role": "system", "content": message.content}
                )
            elif isinstance(message, UserMessage):
                formatted_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, ToolMessage):
                formatted_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": message.tool_call_id,
                        "content": message.content,
                    }
                )
            elif isinstance(message, AssistantMessage):
                if message.tool_calls:
                    assistant_msg = {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [],
                    }

                    for tool_call in message.tool_calls:
                        formatted_tool_call = {
                            "id": tool_call.id
                            or f"call_{len(assistant_msg['tool_calls']) + 1}",
                            "type": "function",
                            "function": {
                                "name": tool_call.name,
                                "arguments": json.dumps(tool_call.arguments),
                            },
                        }
                        assistant_msg["tool_calls"].append(formatted_tool_call)

                    formatted_messages.append(assistant_msg)
                else:
                    formatted_messages.append(
                        {"role": "assistant", "content": message.content}
                    )

        return formatted_messages

    @staticmethod
    async def complete(
        model_spec: ModelSpec,
        messages: list[ModelMessage],
        output_type: Type[T] | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> CompletionResponse[T | str]:
        """
        Generate a completion using Anthropic.

        Args:
            model_spec: The model specification to use.
            messages: List of structured message objects.
            output_type: Optional desired output type (Pydantic model) for structured output.
            tools: Optional list of tools the model can use.

        Returns:
            CompletionResponse containing either content or tool calls.
        """
        logger.debug(
            "anthropicprovider.complete called",
            model_spec=model_spec,
            output_type=output_type,
            has_tools=tools is not None,
        )
        try:
            import anthropic  # noqa: PLC0415
        except ImportError as e:
            logger.exception("anthropic package not installed")
            raise ImportError(
                "Anthropic package is not installed. Install it with 'pip install anthropic'"
            ) from e

        try:
            # Get config from context
            config = get_config()

            # Check if Anthropic config is available
            if (
                not config
                or not config.ai_providers
                or not config.ai_providers.anthropic
            ):
                logger.warning("anthropic configuration is missing in planarconfig")
                raise ValueError(
                    "Anthropic configuration is missing. Please provide Anthropic credentials in your config."
                )

            anthropic_config = config.ai_providers.anthropic
            logger.debug("anthropic client configured from planarconfig")
            # Initialize Anthropic client with credentials from config
            client_kwargs: AnthropicKwargs = {
                "api_key": anthropic_config.api_key.get_secret_value(),
            }

            # Add optional parameters if they exist
            if anthropic_config.base_url:
                client_kwargs["base_url"] = anthropic_config.base_url

            # Initialize client - currently unused in stub implementation
            _ = anthropic.Anthropic(**client_kwargs)
        except (RuntimeError, ValueError) as e:
            # Fallback to environment variables when running outside of HTTP context
            # or when configuration is incomplete
            # client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY from environment
            logger.exception(
                "failed to configure anthropic client from planarconfig or context"
            )
            raise ValueError("Anthropic configuration is missing.") from e

        # Format messages for Anthropic
        file_map = None  # TODO: Implement file map
        formatted_messages = AnthropicProvider.prepare_messages(messages, file_map)

        # Prepare API call parameters
        kwargs = {
            "model": model_spec.model_id,
            "messages": formatted_messages,
            **model_spec.parameters,
        }

        # Handle tools
        if tools:
            formatted_tools = []
            for tool in tools:
                # Convert our Pydantic model to Anthropic's expected format
                schema = tool.parameters
                anthropic_params = {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                }

                formatted_tools.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": anthropic_params,
                    }
                )

            kwargs["tools"] = formatted_tools

        # Handle structured output if output_type is provided
        if output_type is not None:
            if not issubclass(output_type, BaseModel):
                raise ValueError("Non-Pydantic structured output not supported yet.")

            schema_json = output_type.model_json_schema()
            kwargs["system"] = (
                f"You must respond with valid JSON that matches the following schema:\n{schema_json}"
            )

        # This is a stub implementation that would be filled out with the actual API call
        # In a real implementation, would make an API call to Anthropic:
        # message = await client.messages.create(
        #     **kwargs
        # )

        # Process tool calls (stub implementation)
        # if message.content[0].type == "tool_use":
        #     tool_calls = []
        #     for tool_use in message.content:
        #         if tool_use.type == "tool_use":
        #             tool_calls.append(
        #                 ToolCall(
        #                     id=tool_use.id,
        #                     name=tool_use.name,
        #                     arguments=tool_use.input,
        #                 )
        #             )
        #     return CompletionResponse(content=None, tool_calls=tool_calls)
        # else:
        #     content = message.content[0].text

        # For now, return a stub response
        return CompletionResponse(content="Anthropic response", tool_calls=None)


class AnthropicModel(Model):
    """Anthropic-specific model implementation."""

    provider_class = AnthropicProvider
    name = "Anthropic"

    def __init__(self, model_id: str):
        super().__init__(model_id)


class Anthropic:
    # builder of Anthropic models
    @staticmethod
    def model(model_id: str) -> AnthropicModel:
        """Create a model instance for a custom Anthropic model ID."""
        return AnthropicModel(model_id)

    # Class-level models
    claude_3_opus = model("claude-3-opus")
    claude_3_sonnet = model("claude-3-sonnet")
    claude_3_haiku = model("claude-3-haiku")
    claude_sonnet_4_20250514 = model("claude-sonnet-4-20250514")
    claude_opus_4_20250514 = model("claude-opus-4-20250514")
    claude_sonnet_4 = model("claude-sonnet-4")
    claude_opus_4 = model("claude-opus-4")


class GeminiProvider(Provider):
    """Gemini provider implementation using PydanticAI."""

    @staticmethod
    def model(model_id: str) -> "GeminiModel":
        """Create a model instance for a custom Gemini model ID."""
        return GeminiModel(model_id)

    @staticmethod
    def format_tool_response(tool_response: ToolResponse) -> ToolMessage:
        """Format a tool response into a message for Gemini.

        Args:
            tool_response: The tool response to format.

        Returns:
            A formatted tool message.
        """
        return ToolMessage(
            content=tool_response.content,
            tool_call_id=tool_response.tool_call_id or "call_1",
        )

    @staticmethod
    def prepare_messages(
        messages: list[ModelMessage], file_map: FileMap | None = None
    ) -> list[Any]:
        """Prepare messages from Planar representations into the format expected by PydanticAI.

        Args:
            messages: List of structured messages.
            file_map: Optional file map for file content.

        Returns:
            List of messages in PydanticAI format for Gemini.
        """
        pydantic_messages: list[pydantic_ai.ModelMessage] = []

        def append_request_part(part: pydantic_ai.ModelRequestPart):
            last = (
                pydantic_messages[-1]
                if pydantic_messages
                and isinstance(pydantic_messages[-1], pydantic_ai.ModelRequest)
                else None
            )
            if not last:
                last = pydantic_ai.ModelRequest(parts=[])
                pydantic_messages.append(last)
            last.parts.append(part)

        def append_response_part(part: pydantic_ai.ModelResponsePart):
            last = (
                pydantic_messages[-1]
                if pydantic_messages
                and isinstance(pydantic_messages[-1], pydantic_ai.ModelResponse)
                else None
            )
            if not last:
                last = pydantic_ai.ModelResponse(parts=[])
                pydantic_messages.append(last)
            last.parts.append(part)

        for message in messages:
            if isinstance(message, SystemMessage):
                append_request_part(
                    pydantic_ai.SystemPromptPart(content=message.content or "")
                )
            elif isinstance(message, UserMessage):
                user_content: list[pydantic_ai.UserContent] = []
                files: list[FileContent] = []
                if message.files:
                    if not file_map:
                        raise ValueError("File map empty while user message has files.")
                    for file in message.files:
                        if str(file.id) not in file_map.mapping:
                            raise ValueError(
                                f"File {file} not found in file map {file_map}."
                            )
                        files.append(file_map.mapping[str(file.id)])
                for file in files:
                    match file:
                        case Base64Content():
                            user_content.append(
                                pydantic_ai.BinaryContent(
                                    data=base64.b64decode(file.content),
                                    media_type=file.content_type,
                                )
                            )
                        case FileIdContent():
                            raise Exception(
                                "file id handling not implemented yet for Gemini"
                            )
                if message.content is not None:
                    user_content.append(message.content)
                append_request_part(pydantic_ai.UserPromptPart(content=user_content))
            elif isinstance(message, ToolMessage):
                append_request_part(
                    pydantic_ai.ToolReturnPart(
                        tool_name="unknown",  # FIXME: Planar's ToolMessage doesn't include tool name
                        content=message.content,
                        tool_call_id=message.tool_call_id,
                    )
                )
            elif isinstance(message, AssistantMessage):
                if message.content:
                    append_response_part(
                        pydantic_ai.TextPart(content=message.content or "")
                    )
                if message.tool_calls:
                    for tc in message.tool_calls:
                        append_response_part(
                            pydantic_ai.ToolCallPart(
                                tool_name=tc.name, args=tc.arguments
                            )
                        )

        return pydantic_messages

    @staticmethod
    async def _build_file_map(messages: list[ModelMessage]) -> FileMap:
        """Build file map for Gemini, converting files to base64 for multi-modal support."""
        logger.debug("building file map for gemini", num_messages=len(messages))
        file_dict = {}

        for message_idx, message in enumerate(messages):
            if isinstance(message, UserMessage) and message.files:
                logger.debug(
                    "processing files in message for gemini",
                    num_files=len(message.files),
                    message_index=message_idx,
                )
                for file_idx, file in enumerate(message.files):
                    logger.debug(
                        "processing file for gemini",
                        file_index=file_idx,
                        file_id=file.id,
                        content_type=file.content_type,
                    )

                    # For now we are not using uploaded files with Gemini, so convert all to base64
                    if file.content_type.startswith(
                        ("image/", "audio/", "video/", "application/pdf")
                    ):
                        logger.debug(
                            "encoding file to base64 for gemini",
                            filename=file.filename,
                            content_type=file.content_type,
                        )
                        file_dict[str(file.id)] = Base64Content(
                            content=base64.b64encode(await file.get_content()).decode(
                                "utf-8"
                            ),
                            content_type=file.content_type,
                        )
                    else:
                        logger.warning(
                            "unsupported file type for gemini",
                            content_type=file.content_type,
                        )
                        raise ValueError(
                            f"Unsupported file type for Gemini: {file.content_type}"
                        )

        logger.debug("file map built for gemini", num_entries=len(file_dict))
        return FileMap(mapping=file_dict)

    @staticmethod
    async def complete(
        model_spec: ModelSpec,
        messages: list[ModelMessage],
        output_type: Type[T] | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> CompletionResponse[T | str]:
        """
        Generate a completion using Gemini via PydanticAI.

        Args:
            model_spec: The model specification to use.
            messages: List of structured messages.
            output_type: Optional desired output type (Pydantic model) for structured output.
            tools: Optional list of tools the model can use.

        Returns:
            CompletionResponse containing either content or tool calls.
        """
        logger.debug(
            "gemini completion started",
            model_spec=model_spec,
            output_type=output_type,
            has_tools=tools is not None,
        )

        try:
            # Get config from context
            config = get_config()

            # Check if Gemini config is available
            if not config or not config.ai_providers or not config.ai_providers.gemini:
                logger.warning("gemini configuration is missing in planarconfig")
                raise ValueError(
                    "Gemini configuration is missing. Please provide Gemini credentials in your config."
                )

            gemini_config = config.ai_providers.gemini
            logger.debug("gemini configured from planarconfig")

            # PydanticAI handles client initialization internally using GEMINI_API_KEY env var
            # We need to ensure the API key is available in the environment
            import os

            os.environ["GEMINI_API_KEY"] = gemini_config.api_key.get_secret_value()

        except (RuntimeError, ValueError) as e:
            logger.exception(
                "failed to configure gemini client from planarconfig or context"
            )
            raise ValueError("Gemini configuration is missing.") from e

        # Build file map for multi-modal support
        file_map = await GeminiProvider._build_file_map(messages)

        # Format messages for PydanticAI
        pydantic_ai_messages_list = GeminiProvider.prepare_messages(messages, file_map)

        # Prepare model request parameters
        model_request_parameters = PydanticAIModelRequestParameters()

        # Add model-specific parameters
        if model_spec.parameters:
            # Apply any model parameters (temperature, etc.)
            for key, value in model_spec.parameters.items():
                setattr(model_request_parameters, key, value)

        # Handle tools if provided
        if tools:
            pydantic_ai_tools = []
            for tool in tools:
                pydantic_ai_tools.append(
                    PydanticAIToolDefinition(
                        name=tool.name,
                        description=tool.description,
                        parameters_json_schema=tool.parameters,
                    )
                )
            model_request_parameters.function_tools = pydantic_ai_tools

        # Handle structured output if output_type is provided
        if output_type and issubclass(output_type, BaseModel):
            model_request_parameters.output_mode = "native"
            model_request_parameters.output_object = OutputObjectDefinition(
                name=output_type.__name__,
                description=output_type.__doc__ or "",
                json_schema=output_type.model_json_schema(),
            )

        # Make the API call using PydanticAI
        try:
            pydantic_ai_response = await pydantic_ai_model_request(
                model=f"google-gla:{model_spec.model_id}",
                messages=pydantic_ai_messages_list,
                model_request_parameters=model_request_parameters,
            )
            logger.debug("gemini completion successful via pydantic_ai")
        except Exception as e:
            logger.exception("gemini api call failed")
            raise ValueError(f"Gemini API call failed: {e}") from e

        # Process the response
        response_content: Any = None
        response_tool_calls = []

        for part in pydantic_ai_response.parts:
            if isinstance(part, pydantic_ai.TextPart):
                response_content = part.content
            elif isinstance(part, pydantic_ai.ToolCallPart):
                response_tool_calls.append(
                    ToolCall(
                        id=part.tool_call_id,
                        name=part.tool_name,
                        arguments=part.args
                        if isinstance(part.args, dict)
                        else json.loads(part.args or "{}"),
                    )
                )

        # Handle structured output parsing
        if (
            output_type
            and issubclass(output_type, BaseModel)
            and isinstance(response_content, str)
        ):
            try:
                response_content = output_type.model_validate_json(response_content)
            except Exception:
                logger.exception(
                    "failed to parse gemini response into structured output"
                )
                # Keep as string if parsing fails

        logger.debug(
            "gemini completion processed",
            content_type=type(response_content),
            num_tool_calls=len(response_tool_calls),
        )

        return CompletionResponse(
            content=response_content, tool_calls=response_tool_calls or None
        )


class GeminiModel(Model):
    """Gemini-specific model implementation."""

    provider_class = GeminiProvider
    name = "Gemini"

    def __init__(self, model_id: str):
        super().__init__(model_id)


class Gemini:
    """Builder of Gemini models."""

    @staticmethod
    def model(model_id: str) -> GeminiModel:
        """Create a model instance for a custom Gemini model ID."""
        return GeminiModel(model_id)

    # Class-level models
    gemini_2_5_flash = model("gemini-2.5-flash")
    gemini_2_5_pro = model("gemini-2.5-pro")
