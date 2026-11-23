import sqlglot
from sqlglot.errors import ParseError
from states.agentstate_schema import AgentState


def query_agent(state: AgentState):

    print("\nQuery Agent is validating PostgreSQL syntax...")

    query = state["Query"]

    try:
        parsed_queries = sqlglot.parse(
            query,
            read="postgres"
        )

        if len(parsed_queries) != 1 or parsed_queries[0] is None:
            raise ValueError("Expected exactly one SQL statement.")

        print("Query syntax is valid!")

        return {
            "is_valid": True,
            "validation_error": ""
        }

    except (ParseError, ValueError) as error:

        print("Invalid SQL syntax!")
        print("Error:", error)

        return {
            "is_valid": False,
            "validation_error": str(error),
            "retry_count": state["retry_count"] + 1
        }

