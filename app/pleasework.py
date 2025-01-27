import os

os.environ["OPENAI_API_KEY"] = "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"

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