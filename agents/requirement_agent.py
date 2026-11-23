
import os


from dotenv import load_dotenv
from pydantic import BaseModel, Field
from states.agentstate_schema import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import StateGraph, START, END



# Load environment variables
load_dotenv()

model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)



class RequirementOutput(BaseModel):
    Query: str = Field(
        description="A PostgreSQL SQL query that answers the user's question"
    )
MAX_RETRIES = 3


def requirement_agent(state: AgentState):

    print("\nRequirement Agent is working...")

    prompt = ChatPromptTemplate.from_template("""
You are a PostgreSQL SQL query generation agent.

Generate a PostgreSQL SQL query based on the user's question.

Return the SQL query in the Query field.

Rules:
1. Generate valid PostgreSQL syntax.
2. Do not explain the query.
3. Return only the SQL query in the Query field.
4. If a previous query was invalid, correct it using the validation error.
5. Preserve the original user requirement.

User Question:
{question}

Previous Query:
{previous_query}

Validation Error:
{error}
""")

    chain = prompt | model.with_structured_output(RequirementOutput)

    result = chain.invoke({
        "question": state["user_question"],
        "previous_query": state.get("Query", ""),
        "error": state.get("validation_error", "")
    })

    print("\nGenerated Query:")
    print(result.Query)

    return {
        "Query": result.Query,
        "is_valid": False,
        "validation_error": ""
    }

