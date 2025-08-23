from crewai import Task
from agents.multi_agent import MultiAgent

def create_decision_task(executor_task, generator_task):
    return Task(
        description=(
            "Nhận JSON test case từ GeneratorTask và kết quả thực thi từ ExecutorTask.\n\n"
            "Nếu **tất cả step đều pass**:\n"
            "- Đóng vai Code Generator.\n"
            "- Sinh code Playwright TypeScript từ JSON test case.\n\n"
            "Nếu **có step nào fail**:\n"
            "- Đóng vai Reporter.\n"
            "- Tạo báo cáo chi tiết:\n"
            "  * Liệt kê step thất bại, lý do thất bại, và thông tin debug (ví dụ: screenshot nếu có).\n"
            "  * Đề xuất cách khắc phục cụ thể (ví dụ: sửa selector, tăng timeout).\n"
            "  * Đưa ra nhận xét tổng quan về test case."
        ),
        expected_output=(
            "- Nếu PASS → Code Playwright TypeScript dạng chuỗi.\n"
            "- Nếu FAIL → Báo cáo chi tiết dạng chuỗi gồm:\n"
            "  * Danh sách step thất bại với lý do & screenshot (nếu có).\n"
            "  * Gợi ý khắc phục cụ thể.\n"
            "  * Nhận xét tổng quan về test case."
        ),
        agent=MultiAgent,  # chính là MultiAgent
        context=[generator_task, executor_task]
    )
