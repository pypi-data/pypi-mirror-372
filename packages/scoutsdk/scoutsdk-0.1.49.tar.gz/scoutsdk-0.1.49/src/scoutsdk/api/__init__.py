"""API module for the Scout SDK."""

from .api import ScoutAPI, ResponseFormatType
from .assistants import AssistantsAPI, AssistantData, AssistantDataList
from .conversations import ConversationsAPI
from .audio import AudioAPI
from .image import ImageAPI
from .utils import UtilsAPI
from .types.assistants import (
    AssistantResponse,
)
from .types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageTextContent,
    ChatCompletionMessageImageContent,
    ChatCompletionMessagePDFContent,
)
from .types.images import (
    ImageRequest,
    ImageResponse,
    ImageQuality,
    ImageAspectRatio,
    ImageBackground,
)
from .constants import SCOUT_CUSTOM_FUNCTION_CONTENT_TYPE
from .utils import upload_file_to_signed_url
from .deprecated import deprecated


__all__ = [
    "ScoutAPI",
    "SCOUT_CUSTOM_FUNCTION_CONTENT_TYPE",
    "Response",
    "upload_file_to_signed_url",
    "deprecated",
    "ConversationsAPI",
    "AudioAPI",
    "ImageAPI",
    "UtilsAPI",
    # assistants
    "AssistantsAPI",
    "AssistantData",
    "AssistantDataList",
    "AssistantResponse",
    # chat
    "ChatAPI",
    "ResponseFormatType",
    "ChatCompletionMessage",
    "ChatCompletionMessageTextContent",
    "ChatCompletionMessageImageContent",
    "ChatCompletionMessagePDFContent",
    # images
    "ImageRequest",
    "ImageResponse",
    "ImageQuality",
    "ImageAspectRatio",
    "ImageBackground",
]
