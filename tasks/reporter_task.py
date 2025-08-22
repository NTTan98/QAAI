from crewai import Task
from agents.reporter_agent import ReporterAgent

def create_reporter_task(executor_task, generator_task):
    return Task(
        description=(
            "Nhận JSON test case từ GeneratorTask và kết quả thực thi từ ExecutorTask. "
            "Nếu có bất kỳ step nào trong kết quả thực thi fail, tạo báo cáo chi tiết: "
            "- Liệt kê các step thất bại, lý do thất bại, và thông tin debug (như screenshot nếu có). "
            "- Đề xuất cách khắc phục cụ thể cho từng lỗi (ví dụ: sửa selector, tăng timeout). "
            "- Đưa ra nhận xét tổng quan về test case."
        ),
        expected_output=(
            "Báo cáo chi tiết dạng chuỗi, bao gồm: "
            "- Danh sách các step thất bại với lý do và screenshot (nếu có). "
            "- Gợi ý khắc phục cụ thể. "
            "- Nhận xét tổng quan về test case."
        ),
        agent=ReporterAgent,
        context=[generator_task, executor_task]
    )