import os
import pandas as pd
import logging
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_community.tools import tool
from langchain_ollama import ChatOllama
from langchain_experimental.agents import create_pandas_dataframe_agent

logging.basicConfig(level=logging.WARNING)
logging.getLogger("crewai").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)

os.environ["OPENAI_API_KEY"] = "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"

llm = ChatOpenAI(model="gpt-3.5-turbo")

df = pd.read_csv("/mnt/c/Users/USER/crewai-ollama/app/inquiries_data.csv")

agent_executor = create_pandas_dataframe_agent(
    llm,
    df,
    agent_type="openai-tools",
    verbose=False,
    allow_dangerous_code=True
)

@tool
def excel_tool(query: str, *, config: dict = None) -> str:
    """
    This tool processes user queries related to an Excel file.
    It uses the Pandas DataFrame agent to analyze and perform operations on the dataset.
    """
    return agent_executor.invoke(query)

excel_agent = Agent(
    role="Excel Agent",
    goal="Assist with Excel file operations like reading and analyzing data.",
    backstory="""You are an expert in handling Excel files. People rely on you to efficiently process, analyze, 
                 and extract meaningful insights from data in Excel format.""",
    llm=llm,
    tools=[excel_tool],
    verbose=False
)

print("## Welcome to the Excel Assistant")
query = input("What can I assist you with? : ")

excel_task = Task(
    description=f"Load data from the Excel file, process the data, and perform the user query ..... {query}",
    expected_output=f"Perform operations dynamically and return the result....... {query}",
    agent=excel_agent
)

crew = Crew(
    agents=[excel_agent],
    tasks=[excel_task],
    verbose=False
)

result = crew.kickoff()

print("############")
print("Result: ", result)