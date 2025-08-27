from datetime import timedelta
from typing import Any, cast
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.ai import Agent
from planar.ai.agent import (
    AgentRunResult,
)
from planar.ai.agent_utils import create_tool_definition, extract_files_from_model
from planar.ai.models import (
    AgentConfig,
    AssistantMessage,
    CompletionResponse,
    SystemMessage,
    ToolCall,
    ToolMessage,
    UserMessage,
)
from planar.ai.providers import OpenAI
from planar.app import PlanarApp
from planar.config import sqlite_config
from planar.files.models import PlanarFile
from planar.testing.planar_test_client import PlanarTestClient
from planar.workflows.decorators import workflow
from planar.workflows.execution import execute
from planar.workflows.models import Workflow
from planar.workflows.step_core import Suspend, suspend

app = PlanarApp(
    config=sqlite_config(":memory:"),
    title="Planar app for testing agents",
    description="Testing",
)


@pytest.fixture(name="app")
def app_fixture():
    yield app


# Test data and models (not test classes themselves)
# Using different names to avoid pytest collection warnings
class InputModel(BaseModel):
    text: str
    value: int


class OutputModel(BaseModel):
    message: str
    score: int


# Mock data for receipt analysis tests
MOCK_RECEIPT_DATA = {
    "merchant_name": "Coffee Shop",
    "date": "2025-03-11",
    "total_amount": 42.99,
    "items": [
        {"name": "Coffee", "price": 4.99, "quantity": 2},
        {"name": "Pastry", "price": 3.99, "quantity": 1},
    ],
    "payment_method": "Credit Card",
    "receipt_number": "R-123456",
}


@pytest.fixture
def mock_providers():
    """Mock both OpenAI and Anthropic providers to return test responses."""

    # Create a factory to produce provider mocks with consistent tracking
    def create_provider_mock():
        mock = Mock()
        mock.call_count = 0
        return mock

    # Create mocks for each provider
    provider_mocks = {
        "openai": create_provider_mock(),
        "anthropic": create_provider_mock(),
    }

    # Shared mock response generator
    async def generate_response(
        output_type=None, tools=None, planar_files=None, is_first_call=True
    ):
        """Generate appropriate mock responses based on request parameters"""
        # Tool-based multi-turn conversation
        if tools:
            if is_first_call:
                return CompletionResponse(
                    content=None,
                    tool_calls=[
                        cast(
                            ToolCall,
                            {
                                "id": "call_1",
                                "name": "tool1",
                                "arguments": {"param": "test_param"},
                            },
                        )
                    ],
                )
            elif output_type == OutputModel:
                return CompletionResponse(
                    content=OutputModel(message="Multi-turn response", score=90),
                    tool_calls=None,
                )
            else:
                return CompletionResponse(
                    content="Final tool response",
                    tool_calls=None,
                )

        # Planar file processing
        elif planar_files:
            if output_type and issubclass(output_type, BaseModel):
                # If a specific output model is requested, return a predetermined mock instance
                if output_type == OutputModel:
                    return CompletionResponse(
                        content=OutputModel(message="Analyzed file content", score=98),
                        tool_calls=None,
                    )
                else:
                    # Check file content type for different response types
                    file_type = None
                    if len(planar_files) > 0:
                        file_type = planar_files[0].content_type

                    # Generate mock response based on file type
                    if file_type == "application/pdf":
                        mock_data = {**MOCK_RECEIPT_DATA, "document_type": "pdf"}
                    else:  # Image types
                        mock_data = {**MOCK_RECEIPT_DATA, "document_type": "image"}

                    # Only include fields that exist in the model
                    filtered_data = {
                        k: v
                        for k, v in mock_data.items()
                        if k in output_type.model_fields
                    }

                    return CompletionResponse(
                        content=output_type.model_validate(filtered_data),
                        tool_calls=None,
                    )
            else:
                file_type = planar_files[0].content_type if planar_files else None
                if file_type == "application/pdf":
                    return CompletionResponse(
                        content="Description of the PDF document",
                        tool_calls=None,
                    )
                else:
                    return CompletionResponse(
                        content="Description of the image content",
                        tool_calls=None,
                    )

        # Structured output (single turn)
        elif output_type == OutputModel:
            return CompletionResponse(
                content=OutputModel(message="Test", score=95),
                tool_calls=None,
            )

        # Default simple response
        else:
            return CompletionResponse(
                content="Mock LLM response",
                tool_calls=None,
            )

    # Create a factory function for patched provider methods
    def create_provider_patch(provider_key):
        """Create patched complete method for the specified provider"""

        async def patched_complete(*args, **kwargs):
            # Get the provider's mock
            mock = provider_mocks[provider_key]

            # Update call tracking
            mock.call_count += 1
            mock.call_args = (args, kwargs)
            mock.call_args_list.append(cast(Any, (args, kwargs)))

            messages = kwargs.get("messages", [])
            planar_files = None
            for msg in messages:
                if isinstance(msg, UserMessage) and msg.files:
                    planar_files = msg.files
                    break

            # Generate appropriate response
            return await generate_response(
                output_type=kwargs.get("output_type"),
                tools=kwargs.get("tools"),
                planar_files=planar_files,
                is_first_call=(mock.call_count == 1),
            )

        return patched_complete

    # Apply patches
    with (
        patch(
            "planar.ai.providers.OpenAIProvider.complete",
            create_provider_patch("openai"),
        ),
        patch(
            "planar.ai.providers.AnthropicProvider.complete",
            create_provider_patch("anthropic"),
        ),
    ):
        yield (provider_mocks["openai"], provider_mocks["anthropic"])


DEFAULT_CONFIG = AgentConfig(
    system_prompt="Default system prompt",
    user_prompt="Default user prompt: {{ input }}",
    model="openai:gpt-4.1",
    max_turns=3,
)


@pytest.fixture
def mock_get_agent_config():
    """Mock the get_agent_config function to return empty config by default."""
    mock = AsyncMock(return_value=DEFAULT_CONFIG)
    with patch("planar.ai.agent.get_agent_config", mock):
        yield mock


def test_agent_initialization():
    """Test that the Agent class initializes with correct parameters."""
    agent = Agent(
        name="test_agent",
        system_prompt="Test system prompt: {{ param1 }}",
        user_prompt="Test user prompt: {{ param2 }}",
        model="test:model",
        max_turns=3,
    )

    # Verify initialization
    assert agent.name == "test_agent"
    assert agent.system_prompt == "Test system prompt: {{ param1 }}"
    assert agent.user_prompt == "Test user prompt: {{ param2 }}"
    assert agent.model == "test:model"
    assert agent.max_turns == 3
    assert agent.tools == []
    assert agent.input_type is None
    assert agent.output_type is None
    assert agent.model_parameters == {}


async def test_agent_call_simple(session: AsyncSession, mock_providers):
    """Test that an agent can be called in a workflow for a simple string response."""
    openai_mock, anthropic_mock = mock_providers

    # Create an agent
    test_agent = Agent(
        name="test_agent",
        system_prompt="Process this request",
        user_prompt="Input: {{ input }}",
        model="openai:gpt-4.1",  # Using a real provider name
    )

    # Define a workflow that uses the agent
    @workflow()
    async def test_workflow(input_text: str):
        result = await test_agent(input_value=input_text)
        assert isinstance(result, AgentRunResult)
        return result.output

    with patch(
        "planar.ai.agent.get_agent_config",
        AsyncMock(return_value=test_agent.to_config()),
    ) as mock_config:
        # Start and execute the workflow
        wf = await test_workflow.start("test input")
        result = await execute(wf)

        # Verify the result
        assert result == "Mock LLM response"

        # Verify the workflow completed successfully
        updated_wf = await session.get(Workflow, wf.id)
        assert updated_wf is not None
        assert updated_wf.result == "Mock LLM response"

        # Verify get_agent_config was called with the agent name
        assert mock_config.called

        # Verify complete was called with the formatted messages
        assert openai_mock.call_count == 1  # called once
        args, kwargs = openai_mock.call_args
        messages = kwargs.get("messages")
        assert any(
            isinstance(m, SystemMessage) and m.content == "Process this request"
            for m in messages
        )
        assert any(
            isinstance(m, UserMessage) and m.content == "Input: test input"
            for m in messages
        )


async def test_prompt_injection_protection(session: AsyncSession, mock_providers):
    """Ensure unsafe template expressions raise an error before model call."""
    openai_mock, _ = mock_providers

    inj_agent = Agent(
        name="inj_agent",
        system_prompt="Hi",
        user_prompt="{{ input.__class__.__mro__[1] }}",
    )

    @workflow()
    async def inj_workflow(text: str):
        return await inj_agent(text)

    with patch(
        "planar.ai.agent.get_agent_config",
        AsyncMock(return_value=inj_agent.to_config()),
    ):
        wf = await inj_workflow.start("test")
        with pytest.raises(ValueError):
            await execute(wf)

        assert openai_mock.call_count == 0


async def test_agent_with_structured_output(session: AsyncSession, mock_providers):
    """Test agent with structured output using a Pydantic model."""
    openai_mock, anthropic_mock = mock_providers

    # Create an agent with structured output
    test_agent = Agent(
        name="structured_agent",
        system_prompt="Provide structured analysis",
        user_prompt="Analyze: {{ input }}",
        output_type=OutputModel,
        model="openai:gpt-4.1",
    )

    @workflow()
    async def structured_workflow(input_text: str):
        result = await test_agent(input_value=input_text)
        await suspend(interval=timedelta(seconds=0.1))
        return {"message": result.output.message, "score": result.output.score}

    with patch(
        "planar.ai.agent.get_agent_config",
        AsyncMock(return_value=test_agent.to_config()),
    ):
        wf = await structured_workflow.start("test structured input")
        result = await execute(wf)
        assert isinstance(result, Suspend)
        result = await execute(wf)

        assert isinstance(result, dict)
        assert result["message"] == "Test"
        assert result["score"] == 95

        updated_wf = await session.get(Workflow, wf.id)
        assert updated_wf is not None
        assert updated_wf.result == {"message": "Test", "score": 95}

        # Verify the correct provider method was called with right params
        assert openai_mock.call_count == 1  # called once
        args, kwargs = openai_mock.call_args
        assert kwargs["output_type"] == OutputModel
        messages = kwargs["messages"]
        assert any(
            isinstance(m, SystemMessage) and m.content == "Provide structured analysis"
            for m in messages
        )
        assert any(
            isinstance(m, UserMessage) and m.content == "Analyze: test structured input"
            for m in messages
        )


async def test_agent_with_input_validation(
    session: AsyncSession, mock_get_agent_config, mock_providers
):
    """Test agent with input validation using a Pydantic model."""
    openai_mock, anthropic_mock = mock_providers

    # Create an agent with input validation
    test_agent = Agent(
        name="validated_input_agent",
        system_prompt="Process validated input",
        user_prompt="Text: {{ input.text }}, Value: {{ input.value }}",
        input_type=InputModel,
        model="openai:gpt-4.1",
    )

    # Define a workflow that uses the agent
    @workflow()
    async def validation_workflow(input_text: str, input_value: int):
        result = await test_agent(
            input_value=InputModel(text=input_text, value=input_value)
        )
        return result.output

    # Start and execute the workflow
    wf = await validation_workflow.start("test input", 42)
    result = await execute(wf)

    # Verify the result
    assert result == "Mock LLM response"

    # Verify the agent validates input
    # Define a workflow missing the required 'value' parameter
    @workflow()
    async def invalid_workflow(input_text: str):
        # This call should raise a validation error at runtime
        # Ignore the type error to test validation
        return await test_agent(input_value=input_text)  # type: ignore

    # Start the workflow - this doesn't execute the agent validation yet
    invalid_wf = await invalid_workflow.start("missing value")

    # Now actually execute the workflow, which should raise ValueError
    with pytest.raises(ValueError):
        await execute(invalid_wf)


async def test_agent_with_tools(
    mock_providers,
    client: PlanarTestClient,
    app: PlanarApp,
):
    """Test agent with tools for multi-turn conversations."""
    openai_mock, anthropic_mock = mock_providers

    # Define some tools
    async def tool1(param: str) -> str:
        """Test tool 1"""
        return f"Tool 1 result: {param}"

    async def tool2(num: int) -> int:
        """Test tool 2"""
        return num * 2

    # Create an agent with tools
    test_agent = Agent(
        name="tools_agent",
        system_prompt="Use tools to solve the problem",
        user_prompt="Problem: {{ input }}",
        tools=[tool1, tool2],
        output_type=OutputModel,
        max_turns=3,
        model="anthropic:claude-3-sonnet",  # Test the Anthropic provider this time
    )

    # then register it with app
    app.register_agent(test_agent)

    # Define a workflow that uses the agent
    @workflow()
    async def tools_workflow(problem: str):
        result = await test_agent(input_value=problem)
        return {"message": result.output.message, "score": result.output.score}

    with patch(
        "planar.ai.agent.get_agent_config",
        AsyncMock(return_value=test_agent.to_config()),
    ):
        # Start and execute the workflow
        wf = await tools_workflow.start("complex problem")
        result = await app.orchestrator.wait_for_completion(wf.id)

        # Verify the result
        assert isinstance(result, dict)
        assert result["message"] == "Multi-turn response"
        assert result["score"] == 90

        # Verify complete was called twice (once for tool call, once for final response)
        assert anthropic_mock.call_count == 2

        # First call should include tools
        args, first_call_kwargs = anthropic_mock.call_args_list[0]
        assert len(first_call_kwargs["tools"]) == 2
        assert first_call_kwargs["output_type"] == OutputModel

        response = await client.get(
            f"/planar/v1/workflows/{wf.function_name}/runs/{wf.id}/steps"
        )
        data = response.json()

        step = data["items"][0]
        assert step["step_id"] == 1
        assert step["function_name"] == "planar.ai.agent.Agent.run_step"
        assert step["display_name"] == test_agent.name


async def test_config_override(session: AsyncSession, mock_providers):
    """Test that agent correctly applies configuration overrides."""
    openai_mock, anthropic_mock = mock_providers

    # Create a custom mock for agent_config with overrides
    override_config = AgentConfig(
        system_prompt="Overridden system prompt",
        user_prompt="Overridden user prompt: {{ input }}",
        model="anthropic:claude-3-opus",  # Change from OpenAI to Anthropic
        max_turns=5,
    )

    # Create an agent with defaults that will be overridden
    test_agent = Agent(
        name="override_agent",
        system_prompt="Original system prompt",
        user_prompt="Original user prompt: {{ input }}",
        model="openai:gpt-4.1",  # Start with OpenAI
        max_turns=1,
    )

    @workflow()
    async def override_workflow(input_text: str):
        result = await test_agent(input_text)
        return result.output

    with patch(
        "planar.ai.agent.get_agent_config",
        AsyncMock(return_value=override_config),
    ) as mock_config:
        wf = await override_workflow.start("override test")
        result = await execute(wf)

        # Verify the result
        assert result == "Mock LLM response"

        # Verify get_agent_config was called
        assert mock_config.called

        # Since we overrode to anthropic, that provider should be used
        assert anthropic_mock.call_count == 1  # called once
        assert openai_mock.call_count == 0  # not called

        # Verify the messages include the overridden prompts
        args, kwargs = anthropic_mock.call_args
        messages = kwargs["messages"]
        assert any(
            isinstance(m, SystemMessage) and m.content == "Overridden system prompt"
            for m in messages
        )
        assert any(
            isinstance(m, UserMessage)
            and m.content == "Overridden user prompt: override test"
            for m in messages
        )


async def test_agent_with_model_parameters(session: AsyncSession, mock_providers):
    """Test that an agent can be configured with model parameters."""
    openai_mock, anthropic_mock = mock_providers

    # Create an agent with model parameters
    test_agent = Agent(
        name="params_agent",
        system_prompt="Test with parameters",
        user_prompt="Input: {{ input }}",
        model=OpenAI.gpt_4_1,
        model_parameters={"temperature": 0.2, "top_p": 0.95},
    )

    # Define a workflow that uses the agent
    @workflow()
    async def params_workflow(input_text: str):
        result = await test_agent(input_value=input_text)
        return result.output

    with patch(
        "planar.ai.agent.get_agent_config",
        AsyncMock(return_value=test_agent.to_config()),
    ):
        # Start and execute the workflow
        wf = await params_workflow.start("test input")
        result = await execute(wf)

        # Verify the result
        assert result == "Mock LLM response"

        # Check that model parameters were handled correctly
        # (in a real implementation, this would affect the call to the LLM provider)
        assert test_agent.model_parameters == {"temperature": 0.2, "top_p": 0.95}

        # Verify the model parameters are passed to the provider
        args, kwargs = openai_mock.call_args
        assert "temperature" in kwargs.get("model_spec").parameters
        assert kwargs.get("model_spec").parameters["temperature"] == 0.2
        assert kwargs.get("model_spec").parameters["top_p"] == 0.95


async def test_tool_response_formatting(
    session: AsyncSession, mock_get_agent_config, mock_providers
):
    """Test that tool responses are correctly formatted in multi-turn conversations."""
    openai_mock, _ = mock_providers

    # Define a tool that returns a specific response - must match name in mock
    async def tool1(param: str) -> str:
        """Test tool with simple string return"""
        return f"Tool result for: {param}"

    # Create an agent with the tool
    test_agent = Agent(
        name="tool_response_agent",
        system_prompt="Use tools to process the query",
        user_prompt="Query: {{ input }}",
        tools=[tool1],  # Name matches what the mock will call
        model="openai:gpt-4.1",
        max_turns=3,
    )

    # Define a workflow using the agent
    @workflow()
    async def tool_workflow(query: str):
        result = await test_agent(input_value=query)
        return result.output

    # Start and execute the workflow
    wf = await tool_workflow.start("test query")
    result = await execute(wf)

    # Verify result
    assert result == "Final tool response"

    # Verify complete was called twice
    assert openai_mock.call_count == 2

    # Extract the messages from the second call to check for proper tool response formatting
    args, second_call_kwargs = openai_mock.call_args_list[1]
    messages = second_call_kwargs.get("messages")

    # Check that there's a ToolMessage in the conversation
    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1

    # Verify the content of the tool message matches our tool's output
    assert (
        tool_messages[0].content is not None
        and "Tool result for: test_param" in tool_messages[0].content
    )

    # Verify that the message was formatted using the format_tool_response method
    assert tool_messages[0].tool_call_id is not None


async def test_structured_output_with_tools(
    session: AsyncSession, mock_get_agent_config, mock_providers
):
    """Test that structured output works correctly with tool calling."""
    openai_mock, anthropic_mock = mock_providers

    # Define a tool function - must match name in mock
    async def tool1(param: str) -> dict:
        """Fetch data for the given ID"""
        return {"id": param, "value": f"data-{param}"}

    # Create a test agent with structured output and tools
    test_agent = Agent(
        name="structured_tool_agent",
        system_prompt="Process the input and return structured data",
        user_prompt="Process: {{ input }}",
        tools=[tool1],
        output_type=OutputModel,
        model="openai:gpt-4.1",
        max_turns=3,
    )

    # Define workflow
    @workflow()
    async def structured_tool_workflow(data: str):
        result = await test_agent(input_value=data)
        return {"message": result.output.message, "score": result.output.score}

    # Start and execute the workflow
    wf = await structured_tool_workflow.start("test-data")
    result = await execute(wf)

    # Verify result structure
    assert isinstance(result, dict)
    assert result["message"] == "Multi-turn response"
    assert result["score"] == 90

    # Verify calls to complete
    assert openai_mock.call_count == 2

    # Check first call (should include tools and output_type)
    args, first_call_kwargs = openai_mock.call_args_list[0]
    assert first_call_kwargs["output_type"] == OutputModel
    assert len(first_call_kwargs["tools"]) == 1

    # Check second call after tool response
    args, second_call_kwargs = openai_mock.call_args_list[1]
    assert (
        second_call_kwargs["output_type"] == OutputModel
    )  # Should still request structured output

    # Verify messages in second call include the tool response
    messages = second_call_kwargs["messages"]
    assert any(isinstance(m, ToolMessage) for m in messages)

    # Verify assistant message with tool calls is included
    assistant_messages = [
        m for m in messages if isinstance(m, AssistantMessage) and m.tool_calls
    ]
    assert len(assistant_messages) == 1


async def test_tool_error_catching(
    session: AsyncSession, mock_get_agent_config, mock_providers
):
    """Test that workflow can catch and handle errors from tool execution."""
    openai_mock, anthropic_mock = mock_providers

    # Define a tool that raises an exception - must match name in mock
    async def tool1(param: str) -> str:
        """This tool always fails"""
        raise ValueError(f"Tool error for: {param}")

    # Create an agent with the failing tool
    test_agent = Agent(
        name="error_handling_agent",
        system_prompt="Use tools to process this",
        user_prompt="Process: {{ input }}",
        tools=[tool1],
        model="openai:gpt-4.1",
        max_turns=3,
    )

    # Define a workflow that catches the error
    @workflow()
    async def error_handling_workflow(value: str):
        try:
            result = await test_agent(input_value=value)
            return {"status": "success", "output": result.output}
        except ValueError as e:
            # Workflow catches the error and returns a graceful response
            return {"status": "error", "message": str(e)}

    # Start and execute the workflow
    wf = await error_handling_workflow.start("test value")
    result = await execute(wf)

    # Verify the workflow caught the error
    assert isinstance(result, dict)  # Make sure result is a dictionary before indexing
    assert result.get("status") == "error"
    assert "Tool error for:" in result.get("message", "")

    # Verify the API was called once to get the tool call
    assert openai_mock.call_count == 1


def test_tool_validation():
    """Test that different types of functions are supported as tools."""

    # Create some simple Pydantic models for reference
    class ValidToolParams(BaseModel):
        param: str

    class UntypedToolParams(BaseModel):
        param: Any

    # Define a regular function - should work
    async def valid_tool(param: str) -> str:
        """A valid tool function"""
        return f"Result for {param}"

    # This should succeed (not a bound method)
    tool_def = create_tool_definition(valid_tool)
    assert tool_def.name == "valid_tool"
    assert tool_def.description == "A valid tool function"

    # Verify parameter structure
    tool_schema = tool_def.parameters
    reference_schema = ValidToolParams.model_json_schema()

    # Check required fields
    assert tool_schema["required"] == reference_schema["required"]
    # Check param is string type
    assert tool_schema["properties"]["param"]["type"] == "string"

    # Define a function without type annotations - should work
    async def untyped_tool(param):
        """An untyped tool function"""
        return f"Result for {param}"

    # This should succeed with Any type in the schema
    untyped_tool_def = create_tool_definition(untyped_tool)
    assert untyped_tool_def.name == "untyped_tool"
    assert untyped_tool_def.description == "An untyped tool function"

    # Define a class with methods for testing different method types
    class ToolOwner:
        async def bound_method(self, param: str) -> str:
            """A bound instance method"""
            return f"Result for {param}"

        @staticmethod
        async def static_method(param: str) -> str:
            """A static method"""
            return f"Static result for {param}"

        @classmethod
        async def class_method(cls, param: str) -> str:
            """A class method"""
            return f"Class result for {param}"

    # Create an instance and get the bound method
    owner = ToolOwner()
    bound_method = owner.bound_method

    # Test bound instance methods
    bound_tool_def = create_tool_definition(bound_method)
    assert bound_tool_def.name == "bound_method"
    bound_schema = bound_tool_def.parameters
    assert bound_schema["properties"]["param"]["type"] == "string"

    # Test static methods
    static_tool_def = create_tool_definition(ToolOwner.static_method)
    assert static_tool_def.name == "static_method"
    static_schema = static_tool_def.parameters
    assert static_schema["properties"]["param"]["type"] == "string"

    # Test class methods
    class_tool_def = create_tool_definition(ToolOwner.class_method)
    assert class_tool_def.name == "class_method"
    class_schema = class_tool_def.parameters
    assert class_schema["properties"]["param"]["type"] == "string"


# Common models for file-based tests
class ReceiptItem(BaseModel):
    name: str = Field(description="Name of the item")
    price: float | None = Field(description="Price of the item", default=None)
    quantity: int | None = Field(description="Quantity of the item", default=None)


class ReceiptData(BaseModel):
    merchant_name: str = Field(description="Name of the merchant/store")
    date: str = Field(description="Date of the transaction")
    total_amount: float = Field(description="Total amount of the transaction")
    items: list[ReceiptItem] = Field(
        description="List of items purchased with prices if available"
    )
    payment_method: str | None = Field(
        description="Payment method if specified", default=None
    )
    receipt_number: str | None = Field(
        description="Receipt number if available", default=None
    )
    document_type: str | None = Field(
        description="Type of document (pdf or image)", default=None
    )


@pytest.fixture
def planar_files():
    """Create PlanarFile instances for testing."""
    image_file = PlanarFile(
        id=uuid4(),
        filename="receipt.jpg",
        content_type="image/jpeg",
        size=1024,
    )

    pdf_file = PlanarFile(
        id=uuid4(),
        filename="invoice.pdf",
        content_type="application/pdf",
        size=2048,
    )

    return {"image": image_file, "pdf": pdf_file}


async def test_agent_with_direct_planar_file(
    session: AsyncSession, mock_get_agent_config, mock_providers, planar_files
):
    """Test agent with a PlanarFile in a Pydantic input model."""
    openai_mock, anthropic_mock = mock_providers
    image_file = planar_files["image"]

    # Create an agent for receipt analysis
    receipt_agent = Agent(
        name="receipt_analyzer",
        system_prompt="You are an expert receipt analyzer.",
        user_prompt="Please analyze this receipt.",
        output_type=ReceiptData,
        input_type=PlanarFile,
        model=OpenAI.gpt_4_1,
    )

    # Define a workflow using the agent
    @workflow()
    async def receipt_analysis_workflow(file: PlanarFile):
        # Pass it as input_value
        result = await receipt_agent(input_value=file)
        return result.output

    # Start and execute the workflow
    wf = await receipt_analysis_workflow.start(image_file)
    result = await execute(wf)

    # Verify the result is the correct type
    assert isinstance(result, ReceiptData)

    # Verify the result structure
    assert result.merchant_name == "Coffee Shop"
    assert result.date == "2025-03-11"
    assert result.total_amount == 42.99
    assert result.document_type == "image"  # Should detect it's an image
    assert isinstance(result.items, list)
    assert len(result.items) == 2
    assert result.items[0].name == "Coffee"
    assert result.items[0].price == 4.99

    # Verify that provider's complete method was called once
    assert openai_mock.call_count == 1
    args, kwargs = openai_mock.call_args

    # Files are passed in the messages, not directly as planar_files parameter
    messages = kwargs.get("messages", [])
    user_messages = [m for m in messages if isinstance(m, UserMessage)]
    assert len(user_messages) == 1
    assert user_messages[0].files is not None
    assert len(user_messages[0].files) == 1
    assert user_messages[0].files[0] == image_file


class DocumentInput(BaseModel):
    """Model with a single PlanarFile field."""

    file: PlanarFile
    instructions: str | None = None


async def test_agent_with_planar_file_in_model(
    session: AsyncSession, mock_providers, planar_files
):
    """Test agent with a PlanarFile field in a Pydantic model."""
    openai_mock, anthropic_mock = mock_providers
    pdf_file = planar_files["pdf"]

    # Create an agent for document analysis
    document_agent = Agent(
        name="document_analyzer",
        system_prompt="You are an expert document analyzer. Extract all information from the document.",
        user_prompt="Please analyze this document. {{ input.instructions }}",
        output_type=ReceiptData,
        model=OpenAI.gpt_4_1,
        input_type=DocumentInput,
    )

    # Define a workflow using the agent
    @workflow()
    async def document_analysis_workflow(
        file: PlanarFile, instructions: str | None = None
    ):
        input_model = DocumentInput(file=file, instructions=instructions)
        result = await document_agent(input_value=input_model)
        return result.output

    with patch(
        "planar.ai.agent.get_agent_config",
        AsyncMock(return_value=document_agent.to_config()),
    ):
        # Start and execute the workflow with instructions
        wf = await document_analysis_workflow.start(
            pdf_file, instructions="Focus on payment details"
        )
        result = await execute(wf)

        # Verify the result is the correct type
        assert isinstance(result, ReceiptData)

        # Verify the result structure
        assert result.merchant_name == "Coffee Shop"
        assert result.date == "2025-03-11"
        assert result.total_amount == 42.99
        assert result.document_type == "pdf"  # Should detect it's a PDF
        assert isinstance(result.items, list)
        assert len(result.items) == 2

        # Verify that provider's complete method was called once
        assert openai_mock.call_count == 1
        args, kwargs = openai_mock.call_args

        # Files are passed in the messages, not directly as planar_files parameter
        messages = kwargs.get("messages", [])
        user_messages = [m for m in messages if isinstance(m, UserMessage)]
        assert len(user_messages) == 1
        assert user_messages[0].files is not None
        assert len(user_messages[0].files) == 1
        assert user_messages[0].files[0] == pdf_file

        # Verify the user prompt includes the instructions
        messages = kwargs.get("messages", [])
        user_messages = [m for m in messages if isinstance(m, UserMessage)]
        assert len(user_messages) == 1
        assert user_messages[0].content is not None
        assert (
            user_messages[0].content
            == "Please analyze this document. Focus on payment details"
        )


class MultiFileInput(BaseModel):
    """Model with a list of PlanarFile field."""

    files: list[PlanarFile]
    batch_name: str


async def test_agent_with_planar_file_list(
    session: AsyncSession, mock_get_agent_config, mock_providers, planar_files
):
    """Test agent with a list of PlanarFile objects in a Pydantic model."""
    openai_mock, anthropic_mock = mock_providers
    image_file = planar_files["image"]
    pdf_file = planar_files["pdf"]

    # Create an agent for batch document analysis
    batch_agent = Agent(
        name="batch_analyzer",
        system_prompt="You are a batch document processor. Analyze all provided files.",
        user_prompt="Process batch: {{ input.batch_name }}",
        output_type=str,  # Just return a string description
        model=OpenAI.gpt_4_1,
        input_type=MultiFileInput,
    )

    # Define a workflow using the agent
    @workflow()
    async def batch_analysis_workflow(files: list[PlanarFile], batch_name: str):
        # Create a model instance with the file list
        input_model = MultiFileInput(files=files, batch_name=batch_name)
        # Call the agent with the model as input_value
        result = await batch_agent(input_value=input_model)
        return result.output

    with patch(
        "planar.ai.agent.get_agent_config",
        AsyncMock(return_value=batch_agent.to_config()),
    ):
        # Start and execute the workflow with multiple files
        wf = await batch_analysis_workflow.start(
            [image_file, pdf_file], batch_name="Receipt and Invoice"
        )
        result = await execute(wf)

        # Verify the result is a string
        assert isinstance(result, str)
        # Our mock may return either of these responses
        assert result in [
            "Description of the image content",
            "Description of the PDF document",
            "Mock LLM response",
        ]

        # Verify that provider's complete method was called once
        assert openai_mock.call_count == 1
        args, kwargs = openai_mock.call_args

        messages = kwargs.get("messages", [])
        user_messages = [m for m in messages if isinstance(m, UserMessage)]
        assert len(user_messages) == 1
        assert user_messages[0].files is not None
        assert len(user_messages[0].files) == 2
        assert image_file in user_messages[0].files
        assert pdf_file in user_messages[0].files

        # Verify the user prompt includes the batch name
        messages = kwargs.get("messages", [])
        user_messages = [m for m in messages if isinstance(m, UserMessage)]
        assert len(user_messages) == 1
        assert user_messages[0].content == "Process batch: Receipt and Invoice"


def test_extract_files_from_model():
    """Test that files are correctly extracted from Pydantic models."""
    image_file = PlanarFile(
        id=uuid4(),
        filename="test_image.jpg",
        content_type="image/jpeg",
        size=1024,
    )

    pdf_file = PlanarFile(
        id=uuid4(),
        filename="test_document.pdf",
        content_type="application/pdf",
        size=2048,
    )

    # Test model with PlanarFile directly
    files = extract_files_from_model(image_file)
    assert len(files) == 1
    assert files[0] == image_file

    # Test model with PlanarFile as field
    class ModelWithFile(BaseModel):
        name: str
        description: str
        file: PlanarFile
        other_data: int

    model_with_file = ModelWithFile(
        name="Test Model",
        description="A test model with a file",
        file=pdf_file,
        other_data=42,
    )

    files = extract_files_from_model(model_with_file)
    assert len(files) == 1
    assert files[0] == pdf_file

    # Test model with list of PlanarFile objects
    class ModelWithFileList(BaseModel):
        name: str
        files: list[PlanarFile]

    model_with_file_list = ModelWithFileList(
        name="Test Model with File List",
        files=[image_file, pdf_file],
    )

    files = extract_files_from_model(model_with_file_list)
    assert len(files) == 2
    assert image_file in files
    assert pdf_file in files

    # Test mixed list with non-PlanarFile items
    class ModelWithMixedList(BaseModel):
        name: str
        items: list

    model_with_mixed_list = ModelWithMixedList(
        name="Test Model with Mixed List",
        items=[image_file, "not a file", 123, pdf_file],
    )

    files = extract_files_from_model(model_with_mixed_list)
    assert len(files) == 2
    assert image_file in files
    assert pdf_file in files

    # Test model with no files
    class ModelWithoutFiles(BaseModel):
        name: str
        value: int

    model_without_files = ModelWithoutFiles(name="No Files", value=42)
    files = extract_files_from_model(model_without_files)
    assert len(files) == 0

    files = extract_files_from_model("test string")
    assert len(files) == 0

    # Test nested BaseModel structure with PlanarFile
    class NestedModel(BaseModel):
        description: str
        file: PlanarFile

    nested_model = NestedModel(
        description="A nested model with a file",
        file=image_file,
    )

    class AnotherNestedModel(BaseModel):
        data: str
        files: list[PlanarFile]

    class ComplexModel(BaseModel):
        name: str
        first_nested: NestedModel
        second_nested: AnotherNestedModel

    another_nested = AnotherNestedModel(
        data="Some data",
        files=[pdf_file],
    )

    complex_model = ComplexModel(
        name="Complex Model",
        first_nested=nested_model,
        second_nested=another_nested,
    )

    files = extract_files_from_model(complex_model)
    assert len(files) == 2
    assert image_file in files
    assert pdf_file in files


def test_tool_parameter_serialization():
    """Test that tool parameters are correctly serialized to JSON schema."""

    # Create a reference Pydantic model with various parameter types
    class ComplexToolParams(BaseModel):
        str_param: str
        int_param: int
        float_param: float
        bool_param: bool
        list_param: list[str]
        dict_param: dict[str, int]
        union_param: str | int
        optional_param: str | None = None
        untyped_param: Any = None

    # Define a function with various parameter types
    async def complex_tool(
        str_param: str,
        int_param: int,
        float_param: float,
        bool_param: bool,
        list_param: list[str],
        dict_param: dict[str, int],
        union_param: str | int,
        annotated_param: str = Field(description="This is an annotated parameter"),
        optional_param: str | None = None,
        complex_param: ComplexToolParams = Field(
            description="A complex parameter with various types"
        ),
        untyped_param=None,
    ) -> dict[str, Any]:
        """A tool with various parameter types"""
        return {"result": "success"}

    # Create tool definition
    tool_def = create_tool_definition(complex_tool)

    # Verify basic tool properties
    assert tool_def.name == "complex_tool"
    assert tool_def.description == "A tool with various parameter types"

    # Get schema from the tool parameters
    tool_schema = tool_def.parameters

    # Verify schema structure
    assert "properties" in tool_schema
    assert "required" in tool_schema

    # Verify parameter types are correctly mapped
    props = tool_schema["properties"]
    assert props["str_param"]["type"] == "string"
    assert props["int_param"]["type"] == "integer"
    assert props["float_param"]["type"] == "number"
    assert props["bool_param"]["type"] == "boolean"
    assert props["list_param"]["type"] == "array"
    assert props["list_param"]["items"]["type"] == "string"
    assert props["dict_param"]["type"] == "object"
    assert props["dict_param"]["additionalProperties"]["type"] == "integer"
    assert props["union_param"]["anyOf"][0]["type"] == "string"
    assert props["union_param"]["anyOf"][1]["type"] == "integer"
    assert props["annotated_param"]["type"] == "string"
    assert props["annotated_param"]["description"] == "This is an annotated parameter"
    assert props["complex_param"]["$ref"] == "#/$defs/ComplexToolParams"
    assert (
        tool_schema["$defs"]["ComplexToolParams"]
        == ComplexToolParams.model_json_schema()
    )

    # Verify required parameters
    required = tool_schema["required"]
    assert "str_param" in required
    assert "int_param" in required
    assert "float_param" in required
    assert "bool_param" in required
    assert "list_param" in required
    assert "dict_param" in required
    assert "union_param" in required
    assert "optional_param" not in required  # Has default value
    assert "untyped_param" not in required  # Has default value

    # Now we should be able to fully serialize the ToolDefinition
    parsed = tool_def.model_dump(mode="json")

    # Verify the JSON structure is valid
    assert "name" in parsed
    assert "parameters" in parsed
    assert isinstance(parsed["parameters"], dict)

    # Verify parameters were converted to JSON schema
    assert "properties" in parsed["parameters"]
    assert "required" in parsed["parameters"]
    assert parsed["name"] == "complex_tool"
    assert parsed["parameters"]["title"] == "Complex_toolParameters"
