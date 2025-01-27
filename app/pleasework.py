import os

os.environ["OPENAI_API_KEY"] = ""

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

df = pd.read_csv("/mnt/c/Users/USER/crewai-ollama/app/inquiries_data.csv")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agent_executor = create_pandas_dataframe_agent(
    llm,
    df,
    agent_type="openai-tools",
    verbose=True,
    allow_dangerous_code=True
)


queries = [
    "What are the column names in this dataset?",
    "Give me the number of rows and columns in the dataset.",
    "Find the average of the 'Amount' column.",
    "Which inquiry type has the most entries?",
    "tell me a joke"
]

for query in queries:
    response = agent_executor.invoke(query)
    print(f"Query: {query}")
    print(f"Response: {response}\n")