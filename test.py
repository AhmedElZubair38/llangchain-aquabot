from langchain_openai import ChatOpenAI

import os

os.environ["OPENAI_API_KEY"] = "sample"

llm = ChatOpenAI(
    model="llama3.2:latest",
    base_url="http://localhost:11434/v1"
)

# Test query
response = llm("What is the capital of France?")
print(response.content)
