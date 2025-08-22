from crewai import Task
from agents.codegen_agent import CodeGenAgent

def create_codegen_task(executor_task, generator_task):
    return Task(
        description=(
            "Nhận JSON test case từ GeneratorTask và kết quả thực thi từ ExecutorTask. "
            "Nếu tất cả steps trong kết quả thực thi đều pass, sinh code TypeScript cho Playwright dựa trên JSON test case. "
            "Code phải: "
            "- Sử dụng Playwright API (playwright/test). "
            "- Bao gồm các bước tương ứng với test case. "
            "- Có cấu trúc rõ ràng, dễ đọc, với comment mô tả từng bước."
        ),
        expected_output=(
            "Chuỗi code TypeScript hợp lệ, có thể chạy với Playwright, tái hiện các bước trong test case."
        ),
        agent=CodeGenAgent,
        context=[generator_task, executor_task]
    )