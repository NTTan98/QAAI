import os
from crewai import Agent

#Get Google API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GENERATOR_AGENT = Agent(
    name="generator_agent",
    role="test-generator",
    goal="Sinh Json test case từ mô tả feature",
    backstory=(
        "Bạn là một chuyên gia QA Automation. " 
        "Bạn có khả năng phân tích mô tả hệ thống và tạo ra các test case tự động Json."
        "theo format Playwright."
        "Bạn luôn đảm bảo step rõ ràng, có thứ tự hợp lý và dễ chạy tự động."
    ),
    llm="gemini/gemini-2.5-flash",
)