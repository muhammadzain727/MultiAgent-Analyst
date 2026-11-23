from states.agentstate_schema import AgentState


def check_query(state: AgentState):
    MAX_RETRIES = 3
    if state["is_valid"]:
        return "analyst"

    if state["retry_count"] < MAX_RETRIES:
        return "requirement"

    return "stop"