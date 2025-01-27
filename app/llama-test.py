import os
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "sample"

# Initialize LLM
llm = ChatOpenAI(
    model="llama3.2:latest",
    base_url="http://localhost:11434/v1"
)

# Context for the Swimming Academy
context = """You are an AI assistant for Aquasprint Swimming Academy in Dubai. 
    You help answer questions about swimming programs, facilities, and general inquiries.
    Be helpful, professional, and concise in your responses.
    If you're not sure about something, direct users to contact the academy.
    
    Key Information:
    - Location: The Sustainable City, Dubai
    - Hours: Every day 6:00 AM - 10:00 PM
    - Contact: +971542502761, info@aquasprint.ae
    
    Programs Available:
    1. Kids Program (4-14 years)
       - 8 levels, 8 classes per level
       - Group or private classes
       - Focus on water safety
    
    2. Adults Program (14+ years)
       - 8 progressive levels
       - Customized goals
       - Technique and fitness focus
    
    3. Ladies-Only Aqua Fitness
       - Exclusive women's classes
       - Professional female instructors
       - Low-impact workouts
    
    4. Baby & Toddler Program
       - Safe water introduction
       - Parent-child bonding
       - Certified instructors
    
    5. Special Needs Program
       - Specialized coaching
       - Adaptive levels
       - Individual attention
"""

# Information Agent
info_agent = Agent(
    role="Information Agent",
    goal="Provide compelling information or assist with inquiries about Aquasprint Swimming Academy",
    backstory="""
        You are an expert in swimming academies. You know everything about swimming programs, schedules, 
        bookings, and facilities. You can process and analyze inquiries from users.
    """,
    llm=llm,
    context=context
)

# Task for the agent
task1 = Task(
    description="Respond to inquiries about Aquasprint Swimming Academy's programs and services.",
    expected_output="Provide detailed and accurate responses based on the academy's context.",
    agent=info_agent
)

crew = Crew(
    agents=[info_agent],
    tasks=[task1],
    verbose=2
)

# Execute Task
result = crew.kickoff()

# Print Results
print("############")
print(result)
