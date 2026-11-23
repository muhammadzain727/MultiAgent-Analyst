import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

def analyst_agent(query_results):

    if not query_results:
        return "No data available for analysis."

    df = pd.DataFrame([query_results])

    prompt = ChatPromptTemplate.from_template("""
You are a business data analyst for MyFashionHub.

Analyze the following database results.

Data:
{data}

Explain:
1. Important findings
2. Business patterns
3. Potential opportunities
4. Recommendations

Only make conclusions supported by the data.
Do not invent numbers or findings.
""")

    chain = prompt | model

    response = chain.invoke({
        "data": df.to_string(index=False)
    })

    return response
