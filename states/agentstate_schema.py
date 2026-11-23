from typing import TypedDict

class AgentState(TypedDict):
    user_question: str
    Query: str
    is_valid: bool
    validation_error: str
    retry_count: int
    final_response: str