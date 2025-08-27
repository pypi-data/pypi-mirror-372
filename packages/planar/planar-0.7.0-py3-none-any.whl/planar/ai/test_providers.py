import json
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

import pytest
from pydantic import BaseModel, SecretStr

from planar.ai.models import (
    AssistantMessage,
    Base64Content,
    FileIdContent,
    FileMap,
    ModelMessage,
    SystemMessage,
    ToolCall,
    ToolMessage,
    ToolResponse,
    UserMessage,
)
from planar.ai.providers import Anthropic, ModelSpec, OpenAI, OpenAIProvider
from planar.config import (
    AIProvidersConfig,
    AppConfig,
    OpenAIConfig,
    PlanarConfig,
    SQLiteConfig,
)
from planar.files.models import PlanarFile
from planar.session import config_var


class DummyOutput(BaseModel):
    value: str
    score: int


class DummyGenericOutput[T: BaseModel](BaseModel):
    value: T


# Mock classes for OpenAI client
class MockResponse:
    def __init__(
        self, content="Test response", tool_calls=None, structured_output=None
    ):
        message_content = (
            structured_output if structured_output is not None else content
        )
        self.choices = [
            Mock(message=Mock(content=message_content, tool_calls=tool_calls))
        ]


class MockCompletions:
    def __init__(self):
        self.captured_kwargs = None

    async def create(self, **kwargs):
        self.captured_kwargs = kwargs
        return MockResponse()


class MockBetaCompletions:
    def __init__(self):
        self.captured_kwargs = None

    async def parse(self, response_format=None, **kwargs):
        """Handle structured output parsing"""
        self.captured_kwargs = kwargs.copy()
        self.captured_kwargs["response_format"] = response_format
        # If there's a response_format, create structured output based on it
        if response_format:
            if hasattr(response_format, "model_validate"):
                # Create an instance of the response format model with test data
                if response_format == DummyGenericOutput[DummyOutput]:
                    structured_output = DummyGenericOutput[DummyOutput](
                        value=DummyOutput(value="test value", score=95)
                    )
                else:
                    # Generic values for any other model
                    structured_output = response_format.model_validate(
                        {"value": "test", "score": 100}
                    )
                return MockResponse(structured_output=structured_output)
        return MockResponse()


class MockChat:
    def __init__(self):
        self.completions = MockCompletions()


class MockBetaChat:
    def __init__(self):
        self.completions = MockBetaCompletions()


class MockBeta:
    def __init__(self):
        self.chat = MockBetaChat()


class MockClient:
    def __init__(self, **kwargs):
        self.chat = MockChat()
        self.beta = MockBeta()


@pytest.fixture(name="mock_openai_client")
def mock_openai_client_fixture(monkeypatch):
    """Set up a mock OpenAI client for testing."""
    mock_client = MockClient()
    monkeypatch.setattr("openai.AsyncOpenAI", lambda **kwargs: mock_client)
    return mock_client


@pytest.fixture(name="fake_config")
def fake_config_fixture():
    """Set up a fake config for testing."""
    # Create a minimal PlanarConfig for testing
    # We're using actual PlanarConfig classes to maintain type compatibility
    # Create config objects
    openai_config = OpenAIConfig(
        api_key=SecretStr("mock_key"),
        base_url="https://api.openai.com/v1",
        organization=None,
    )

    ai_providers = AIProvidersConfig(openai=openai_config)

    # Create a minimal valid PlanarConfig for testing
    mock_config = PlanarConfig(
        db_connections={"app": SQLiteConfig(path=":memory:")},
        app=AppConfig(db_connection="app"),
        ai_providers=ai_providers,
    )

    # Set the config in the context variable
    token = config_var.set(mock_config)
    yield mock_config
    # Reset when done
    config_var.reset(token)


class TestOpenAIProvider:
    """Test suite for the OpenAIProvider implementation."""

    def test_format_tool_response(self):
        """Test that tool responses are correctly formatted."""
        # Test with all fields
        response1 = ToolResponse(tool_call_id="call_123", content="Test result")
        message1 = OpenAIProvider.format_tool_response(response1)

        assert isinstance(message1, ToolMessage)
        assert message1.tool_call_id == "call_123"
        assert message1.content == "Test result"

        # Test with missing ID (should generate default)
        response2 = ToolResponse(content="Another result")
        message2 = OpenAIProvider.format_tool_response(response2)

        assert isinstance(message2, ToolMessage)
        assert message2.tool_call_id == "call_1"  # Default ID
        assert message2.content == "Another result"

    def test_format_messages(self):
        """Test that messages are correctly formatted for the OpenAI API."""
        # Create a list of different message types
        messages: list[ModelMessage] = [
            SystemMessage(content="You are a helpful assistant"),
            UserMessage(
                content="Hello",
                files=[
                    PlanarFile(
                        id=UUID("11111111-1111-1111-1111-111111111111"),
                        filename="test_image.jpg",
                        content_type="image/jpeg",
                        size=1024,
                    ),
                    PlanarFile(
                        id=UUID("22222222-2222-2222-2222-222222222222"),
                        filename="test_doc.pdf",
                        content_type="application/pdf",
                        size=2048,
                    ),
                ],
            ),
            AssistantMessage(content="How can I help?"),
            ToolMessage(tool_call_id="call_1", content="Tool result"),
            AssistantMessage(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_2",
                        name="test_tool",
                        arguments={"param1": "value1"},
                    )
                ],
            ),
        ]

        file_map = FileMap(
            mapping={
                "11111111-1111-1111-1111-111111111111": Base64Content(
                    content_type="image/jpeg", content="fake content"
                ),
                "22222222-2222-2222-2222-222222222222": FileIdContent(
                    content="file-123"
                ),
            }
        )
        # Format the messages
        formatted = OpenAIProvider.prepare_messages(messages, file_map)

        # Check the results
        assert len(formatted) == 5

        # Check system message
        assert formatted[0] == {
            "role": "system",
            "content": "You are a helpful assistant",
        }

        # Check user message - note that content is now a list with text item
        assert formatted[1]["role"] == "user"
        assert isinstance(formatted[1]["content"], list)
        assert len(formatted[1]["content"]) == 3
        assert formatted[1]["content"] == [
            {
                "image_url": {"url": "data:image/jpeg;base64,fake content"},
                "type": "image_url",
            },
            {"file": {"file_id": "file-123"}, "type": "file"},
            {"text": "Hello", "type": "text"},
        ]

        # Check assistant message
        assert formatted[2] == {"role": "assistant", "content": "How can I help?"}

        # Check tool message
        assert formatted[3] == {
            "role": "tool",
            "tool_call_id": "call_1",
            "content": "Tool result",
        }

        # Check assistant message with tool calls
        assert formatted[4]["role"] == "assistant"
        assert formatted[4]["content"] is None
        assert len(formatted[4]["tool_calls"]) == 1
        assert formatted[4]["tool_calls"][0]["id"] == "call_2"
        assert formatted[4]["tool_calls"][0]["type"] == "function"
        assert formatted[4]["tool_calls"][0]["function"]["name"] == "test_tool"
        # Verify JSON arguments
        tool_args = json.loads(formatted[4]["tool_calls"][0]["function"]["arguments"])
        assert tool_args == {"param1": "value1"}

    def test_tool_call_with_missing_id(self):
        """Test that tool calls without IDs get auto-generated IDs."""
        # Create a message with tool calls that have no IDs
        message = AssistantMessage(
            content=None,
            tool_calls=[
                ToolCall(
                    name="tool1",
                    arguments={"arg1": "val1"},
                ),
                ToolCall(
                    name="tool2",
                    arguments={"arg2": "val2"},
                ),
            ],
        )

        # Format the message
        formatted = OpenAIProvider.prepare_messages([message])

        # Check that IDs were auto-generated
        assert len(formatted) == 1
        assert formatted[0]["role"] == "assistant"
        assert len(formatted[0]["tool_calls"]) == 2
        assert formatted[0]["tool_calls"][0]["id"] == "call_1"
        assert formatted[0]["tool_calls"][1]["id"] == "call_2"

    def test_model_spec_handling(self):
        """Test that ModelSpec is correctly initialized and parameters are handled."""
        # Create a model spec with parameters
        spec = ModelSpec(
            model_id="gpt-4.1", parameters={"temperature": 0.7, "top_p": 0.95}
        )

        # Check values
        assert spec.model_id == "gpt-4.1"
        assert spec.parameters == {"temperature": 0.7, "top_p": 0.95}

        # Test updating parameters
        spec.parameters["temperature"] = 0.5
        assert spec.parameters["temperature"] == 0.5

    def test_model_str_and_repr(self):
        """Test that Model can be converted to a string and repr."""
        spec = OpenAI.gpt_4_1
        assert str(spec) == "OpenAI:gpt-4.1"
        assert repr(spec) == "OpenAI:gpt-4.1"

        spec = OpenAI.gpt_4_turbo
        assert str(spec) == "OpenAI:gpt-4-turbo"
        assert repr(spec) == "OpenAI:gpt-4-turbo"

        spec = Anthropic.claude_3_haiku
        assert str(spec) == "Anthropic:claude-3-haiku"
        assert repr(spec) == "Anthropic:claude-3-haiku"

        spec = Anthropic.claude_sonnet_4_20250514
        assert str(spec) == "Anthropic:claude-sonnet-4-20250514"
        assert repr(spec) == "Anthropic:claude-sonnet-4-20250514"

        spec = Anthropic.claude_opus_4_20250514
        assert str(spec) == "Anthropic:claude-opus-4-20250514"
        assert repr(spec) == "Anthropic:claude-opus-4-20250514"

        spec = Anthropic.claude_sonnet_4
        assert str(spec) == "Anthropic:claude-sonnet-4"
        assert repr(spec) == "Anthropic:claude-sonnet-4"

        spec = Anthropic.claude_opus_4
        assert str(spec) == "Anthropic:claude-opus-4"
        assert repr(spec) == "Anthropic:claude-opus-4"

    async def test_planar_files(self, fake_config, mock_openai_client):
        """Test that PlanarFile objects are correctly handled and formatted."""
        # Create PlanarFile test objects
        image_file = PlanarFile(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            filename="test_image.jpg",
            content_type="image/jpeg",
            size=1024,
        )

        pdf_file = PlanarFile(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            filename="test_doc.pdf",
            content_type="application/pdf",
            size=2048,
        )

        messages = [
            SystemMessage(content="You are a helpful assistant"),
            UserMessage(content="Describe this file", files=[image_file]),
        ]

        # Configure mock to return a specific response
        file_response = "This is a file description"
        mock_openai_client = Mock()
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=MockResponse(content=file_response)
        )
        mock_openai_client.files = Mock()
        mock_openai_client.files.create = AsyncMock(return_value=Mock(id="file-123"))
        mock_openai_client.beta = Mock()
        mock_openai_client.beta.chat = Mock()
        mock_openai_client.beta.chat.completions = Mock()

        # Replace the original mock with our configured one
        with (
            patch(
                "planar.files.models.PlanarFile.get_content",
                AsyncMock(return_value=b"fake content"),
            ),
            patch(
                "planar.files.models.PlanarFile.get_metadata",
                AsyncMock(return_value=None),
            ),
            pytest.MonkeyPatch().context() as m,
        ):
            m.setattr("openai.AsyncOpenAI", lambda **kwargs: mock_openai_client)

            # Test with a single image file
            result = await OpenAIProvider.complete(
                model_spec=ModelSpec(model_id="gpt-4.1"),
                messages=messages,
            )

            # Verify the returned value
            assert result.content == file_response
            assert result.tool_calls is None

            # Test with multiple files
            # Create a new message with multiple files
            messages[-1] = UserMessage(
                content="Describe these files", files=[image_file, pdf_file]
            )

            multiple_file_response = "This describes multiple files"
            mock_openai_client.chat.completions.create = AsyncMock(
                return_value=MockResponse(content=multiple_file_response)
            )

            # Make the API call with multiple files
            result = await OpenAIProvider.complete(
                model_spec=ModelSpec(model_id="gpt-4.1"),
                messages=messages,
            )

            # Verify the returned value
            assert result.content == multiple_file_response
            assert result.tool_calls is None

            # Test with both files and structured output
            class FileOutput(BaseModel):
                description: str

            structured_file_result = FileOutput(
                description="A PDF document",
            )

            mock_openai_client.beta.chat.completions.parse = AsyncMock(
                return_value=MockResponse(structured_output=structured_file_result)
            )

            # Make the API call with file and structured output
            result = await OpenAIProvider.complete(
                model_spec=ModelSpec(model_id="gpt-4.1"),
                messages=messages,
                output_type=FileOutput,
            )

            # Verify the structured output with file
            assert isinstance(result.content, FileOutput)
            assert result.content.description == "A PDF document"

    async def test_structured_output(self, fake_config, mock_openai_client):
        """Test that structured output is correctly handled."""
        # Create test messages
        messages = [
            SystemMessage(content="You are a helpful assistant"),
            UserMessage(content="Analyze this data"),
        ]

        # Test structured output with DummyOutput model
        result = await OpenAIProvider.complete(
            model_spec=ModelSpec(model_id="gpt-4.1"),
            messages=messages,
            output_type=DummyGenericOutput[DummyOutput],
        )

        # Verify the completion method used
        assert mock_openai_client.beta.chat.completions.captured_kwargs is not None
        captured_kwargs = mock_openai_client.beta.chat.completions.captured_kwargs

        # Verify the output is of the correct type
        assert isinstance(result.content, DummyGenericOutput)
        assert result.content.value == DummyOutput(value="test value", score=95)
        assert result.tool_calls is None

        # Verify the response_format parameter was correctly set
        assert "response_format" in captured_kwargs
        assert captured_kwargs["response_format"] == DummyGenericOutput[DummyOutput]
        # Verify we're sanitizing the name correctly as OpenAI expects
        assert (
            captured_kwargs["response_format"].__name__
            == "DummyGenericOutput_DummyOutput_"
        )
