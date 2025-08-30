from typing import Dict, List, Optional

from pydantic import BaseModel


class SnowglobeData(BaseModel):
    conversation_id: str
    test_id: str


class SnowglobeMessage(BaseModel):
    role: str
    content: str
    snowglobe_data: Optional[SnowglobeData] = None


class CompletionFunctionOutputs(BaseModel):
    response: str


class CompletionRequest(BaseModel):
    messages: List[SnowglobeMessage]

    def to_openai_messages(self) -> List[Dict]:
        """Return a list of OpenAI messages from the Snowglobe messages"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]


class RiskEvaluationRequest(BaseModel):
    messages: List[SnowglobeMessage]


class RiskEvaluationOutputs(BaseModel):
    triggered: bool
    tags: Optional[Dict[str, str]] = None
    reason: Optional[str] = None
    severity: Optional[int] = None
