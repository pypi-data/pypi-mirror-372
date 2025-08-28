# response class
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime

class LLMResponse(BaseModel):
    '''Response from an LLM Provider'''
    content: str = Field(description='The main response content')
    model: str = Field(description='Model that generated the response')
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    usage: Optional[dict[str, Any]] = Field(
        default=None,
        description='Usage statistics (tokens, etc.)'
    )
    finish_reason: Optional[str] = Field(
        default=None,
        description='Reason the model stopped generating'
    )
    response_time_ms: Optional[float] = Field(
        default=None,
        description='Time taken to generate response'
    )
