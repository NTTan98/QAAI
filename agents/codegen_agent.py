import os
from crewai import Agent

#Get Google API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CodeGenAgent = Agent(
    role="Code Generator",
    goal="Sinh code TypeScript từ test case JSON đã pass",
    backstory="Chuyên gia lập trình TypeScript, chuyển đổi các bước test tự động thành code Playwright TypeScript.",
    llm="gemini/gemini-1.5-flash",
)