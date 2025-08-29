from pydantic import BaseModel
from snowcell.schemas.common import Usage

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatChoice(BaseModel):
    index: int | None = None
    message: ChatMessage
    finish_reason: str | None = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatChoice]
    usage: Usage | None = None

