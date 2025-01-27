from langchain_core.tools import tool
import pandas as pd

@tool
def excel():
    """This reads an excel file and all the worksheets inside it. do what the user asks you to"""
    df = pd.read_excel("/mnt/c/Users/USER/crewai-ollama/app/inquiries_data.xlsx")

    # do what the user asks you to

    return df