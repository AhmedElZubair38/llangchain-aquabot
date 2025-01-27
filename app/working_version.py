import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
# print(api_key)

import pandas as pd
from typing import List
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
 
df = pd.read_csv("/mnt/c/Users/USER/crewai-ollama/app/inquiries_data.csv")
 
@tool
def validate_user(user_id: int, addresses: List[str]) -> str:
    """Validate user using historical addresses.
 
    Args:
        user_id (int): The user ID.
        addresses (List[str]): Previous addresses as a list of strings.
    Returns:
        str: Validation result message.
    """
    return f"User {user_id} validated successfully with addresses: {addresses}"
 
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
 
agent_executor = create_pandas_dataframe_agent(
    llm,
    df,
    agent_type="openai-tools",
    verbose=True,
    allow_dangerous_code=True,
    extra_tools=[validate_user]
)
 
queries = [
    "Could you validate user 123? They previously lived at 123 Fake St in Boston MA and 234 Pretend Boulevard in Houston TX.",
    "What are the column names in this dataset?",
    "Give me the number of rows and columns in the dataset.",
    "Which inquiry type has the most entries?",
    "tell me a joke",
    "add a new recird where the name is khalid, the phone number is 9715747448448, and the interested program is the adults program"
]
 
for query in queries:
    response = agent_executor.invoke(query)
    print(f"Query: {query}")
    print(f"Response: {response}\n")