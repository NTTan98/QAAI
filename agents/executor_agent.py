from crewai import Agent
from tools.run_playwright import PlaywrightTestTool
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

playwright_test_tool = PlaywrightTestTool()

ExecutorAgent = Agent(
    name="executor_agent",
    role="Test Executor",
    goal="Nhận JSON test case từ input và chạy thử bằng Playwright, trả kết quả chi tiết.",
    backstory=(
        "Bạn là một QA Automation Engineer chuyên nghiệp. "
        "Bạn có khả năng thực thi các test case tự động trên trình duyệt bằng Playwright. "
        "Bạn luôn cung cấp báo cáo chi tiết về kết quả test execution bao gồm "
        "số steps pass/fail, lý do fail, và screenshot khi cần thiết."
    ),
    llm="gemini/gemini-1.5-flash",
    tools=[playwright_test_tool],
)
