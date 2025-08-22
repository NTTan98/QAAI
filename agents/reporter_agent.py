import os
from crewai import Agent

#Get Google API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ReporterAgent = Agent(
    role="Reporter",
    goal="Tạo báo cáo chi tiết khi test case thất bại, cung cấp lý do và gợi ý khắc phục",
    backstory="Chuyên gia phân tích lỗi test case, cung cấp feedback dễ hiểu cho người dùng.",
    llm="gemini/gemini-1.5-flash",
)