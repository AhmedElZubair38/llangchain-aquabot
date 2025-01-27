import os
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from Exceltool import Excel


os.environ["OPENAI_API_KEY"] = "sample"

llm = ChatOpenAI(
    model="llama3.2:latest",
    base_url="http://localhost:11434/v1"
)

info_agent = Agent(
    role="Information Agent",
    goal="Give compelling information about a certain topic",
    backstory="""
        You love to know information.  People love and hate you for it.  You win most of the
        quizzes at your local pub.
    """,
    llm=llm,
    tools=[Excel]
)

task1 = Task(
    description="Tell me all about the box jellyfish.",
    expected_output="Give me a quick summary and then also give me 7 bullet points describing it.",
    agent=info_agent
)

crew = Crew(
    agents=[info_agent],
    tasks=[task1],
    verbose=2
)

result = crew.kickoff()

print("############")
print(result)