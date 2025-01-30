from langchain_openai import ChatOpenAI

import os

os.environ["OPENAI_API_KEY"] = "sample"

llm = ChatOpenAI(
    model="deepseek-llm",
    base_url="http://172.27.240.1:11434/v1", verbose=True
)

response = llm.invoke("What is the capital of France?")
print(response.content)