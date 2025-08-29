from pydantic import BaseModel
from snowcell.schemas.common import Usage


class CompletionChoice(BaseModel):
    index: int | None = None
    text: str
    finish_reason: str | None = None


class CompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[CompletionChoice]
    usage: Usage | None = None
