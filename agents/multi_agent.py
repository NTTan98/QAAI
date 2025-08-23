import os
from crewai import Agent

#Get Google API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLL_MODEL = os.getenv("LLL_MODEL")

MultiAgent = Agent(
    role="Multi-purpose Agent",
    goal="Tuỳ theo kết quả test case (PASS/FAIL), đóng vai trò Code Generator hoặc Reporter.",
    backstory=(
        "Bạn là một chuyên gia đa năng: "
        "- Khi test case PASS, bạn là Code Generator, sinh code TypeScript từ JSON. "
        "- Khi test case FAIL, bạn là Reporter, phân tích lỗi và gợi ý khắc phục."
    ),
    llm=LLL_MODEL,
)