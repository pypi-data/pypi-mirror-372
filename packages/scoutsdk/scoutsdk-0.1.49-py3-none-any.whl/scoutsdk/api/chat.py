import json
from typing import Any, Optional, Type, overload, TypeVar
from pydantic import BaseModel
from .request_utils import RequestUtils
from scouttypes.chat import (
    ChatCompletionResponse,
    ChatCompletionRequest,
)
from scouttypes.conversations import (
    StreamFinishReason,
    StreamError,
    MessageRole,
    ConversationMessage,
)

DEFAULT_MODEL = "gpt-4o"

ChatCompletionResponseType = TypeVar("ChatCompletionResponseType", bound=BaseModel)


class ChatAPI:
    def __init__(self, base_url: str, headers: dict) -> None:
        self._base_url = base_url
        self._headers = headers

    @overload
    def completion(
        self,
        messages: list[ConversationMessage] | str,
        response_format: Type[ChatCompletionResponseType],
        model: Optional[str] = None,
        assistant_id: Optional[str] = None,
        stream: bool = False,
        debug: Optional[bool] = False,
        allowed_tools: Optional[list[str]] = None,
        llm_args: Optional[dict] = None,
    ) -> ChatCompletionResponseType: ...

    @overload
    def completion(
        self,
        messages: list[ConversationMessage] | str,
        response_format: Optional[None] = None,
        model: Optional[str] = None,
        assistant_id: Optional[str] = None,
        stream: bool = False,
        debug: Optional[bool] = False,
        allowed_tools: Optional[list[str]] = None,
        llm_args: Optional[dict] = None,
    ) -> ChatCompletionResponse: ...

    def completion(
        self,
        messages: list[ConversationMessage] | str,
        response_format: Optional[Type[ChatCompletionResponseType]] = None,
        model: Optional[str] = None,
        assistant_id: Optional[str] = None,
        stream: bool = False,
        debug: Optional[bool] = False,
        allowed_tools: Optional[list[str]] = None,
        llm_args: Optional[dict] = None,
    ) -> ChatCompletionResponseType | ChatCompletionResponse:
        """
        Send a chat completion request to the Scout API.

        Args:
            messages (list[ConversationMessage] | str): The list of chat messages or a single user message string.
            response_format (Optional[Type[ChatCompletionResponseType]]): Pydantic model to use for response validation.
            model (str): The model to use for completion (default: "gpt-4o").
            assistant_id (Optional[str]): The assistant ID to use for the request.
            stream (bool): Whether to stream the response (default: False).
            debug (Optional[bool]): If True, print the payload for debugging.
            allowed_tools (Optional[list[str]]): List of allowed tools for the assistant. None = Use all available tools, Empty list = No tools.
            llm_args (Optional[dict]): Additional arguments to pass to the LLM API.

        Returns:
            ChatCompletionResponseType | ChatCompletionResponse: If response_format is provided, returns a validated instance of the specified ChatCompletionResponseType model. Otherwise, returns a ChatCompletionResponse object.

        Raises:
            Exception: If there is an error processing the response, especially when response_format is used.
        """

        if isinstance(messages, str):
            messages = [ConversationMessage(role=MessageRole.USER, content=messages)]

        request_payload = ChatCompletionRequest(
            messages=messages,
            model=model or DEFAULT_MODEL,
            assistant_id=assistant_id,
            stream=stream,
            allowed_tools=allowed_tools,
            llm_args=llm_args,
            response_format=response_format.model_json_schema()
            if response_format
            else None,
        )

        json_payload = request_payload.model_dump(exclude_none=True)
        if debug:
            print(f"payload: {json_payload}")

        response, status_code = RequestUtils.post(
            url=f"{self._base_url}/api/chat/completion/",
            headers=self._headers,
            json_payload=json_payload,
            stream=stream,
        )

        if stream:
            chat_completion_response = self._convert_streaming_response(response)
        else:
            chat_completion_response = ChatCompletionResponse.model_validate(response)

        if response_format:
            # extract the last message from the response to ignore tools calls
            try:
                if not chat_completion_response.messages:
                    raise ValueError("No messages in response to extract content from")
                content = chat_completion_response.messages[-1].content
                # todo handle other content types
                if not isinstance(content, str):
                    raise ValueError(
                        f"Expected string content for response format parsing, got {type(content)}"
                    )
                return response_format.model_validate(json.loads(content))
            except Exception as e:
                raise Exception(f"Error processing Response: {response}") from e

        return chat_completion_response

    def _convert_streaming_response(self, response: Any) -> ChatCompletionResponse:
        if not isinstance(response, dict):
            message_data = {"role": "assistant", "content": str(response)}
            return ChatCompletionResponse(
                messages=[ConversationMessage.model_validate(message_data)]
            )

        if response.get("finish_reason", "") == StreamFinishReason.ERROR:
            error_data = response.get("error")
            # Handle case where error field is None or missing
            if error_data is None:
                # Create a default error if none is provided
                error = StreamError(
                    error_code="unknown_error",
                    reference_id="",
                    message="An error occurred but no error details were provided",
                )
            else:
                try:
                    error = StreamError.model_validate(error_data)
                except Exception as e:
                    # If error validation fails, create a fallback error
                    error = StreamError(
                        error_code="validation_error",
                        reference_id="",
                        message=f"Error validation failed: {str(e)}",
                    )

            return ChatCompletionResponse(messages=[], error=error)

        return ChatCompletionResponse(
            messages=[ConversationMessage.model_validate(response)]
        )
