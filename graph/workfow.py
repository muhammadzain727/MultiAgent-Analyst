import os
from typing import TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from states.agentstate_schema import AgentState
from langgraph.graph import StateGraph, START, END
from graph.routing import check_query
from agents.requirement_agent import requirement_agent, RequirementOutput
from agents.query_agent import query_agent
from agents.analyst_agent import analyst_agent
import sqlglot
from sqlglot.errors import ParseError


# Load environment variables
load_dotenv()


# Initialize LLM
model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

workflow = StateGraph(AgentState)

# Register nodes
workflow.add_node("requirement_agent", requirement_agent)
workflow.add_node("query_agent", query_agent)
workflow.add_node("analyst_agent", analyst_agent)

# Define edges
workflow.add_edge(START, "requirement_agent")

workflow.add_edge(
    "requirement_agent",
    "query_agent"
)

# Conditional edges
workflow.add_conditional_edges(
    "query_agent",
    check_query,
    {
        "analyst": "analyst_agent",
        "requirement": "requirement_agent",
        "stop": END
    }
)

workflow.add_edge("analyst_agent", END)

# Compile graph
app = workflow.compile()


    