from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def requirement_agent(user_question):

    prompt = f"""
    Understand the following business question.

    Question: {user_question}

    Identify:
    1. Required data
    2. Required metrics
    3. Analysis type
    """

    response = llm.invoke(prompt)

    return response.content