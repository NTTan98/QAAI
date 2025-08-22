from crewai import Task
from agents.executor_agent import ExecutorAgent

def create_executor_task(generator_task):
    return Task(
        description=(
            "Bạn sẽ nhận được một JSON test case từ output của . "
            "Nhiệm vụ của bạn là: "
            "1. Kiểm tra format JSON test case hợp lệ "
            "2. Sử dụng PlaywrightTestTool để thực thi các steps trong test case "
            "3. Trả về báo cáo chi tiết về kết quả execution"
        ),
        expected_output=(
            "Báo cáo chi tiết về kết quả test execution bao gồm: "
            "- Tổng số steps đã thực thi "
            "- Số steps pass và số steps fail "
            "- Chi tiết từng step: action, kết quả, và lý do pass/fail "
            "- Thông tin về screenshots nếu có lỗi "
            "- Tóm tắt tổng quan về test case (passed/failed) "
            "- Đề xuất fix nếu có steps fail"
        ),
        agent=ExecutorAgent,
        context=[generator_task]  # Lấy output của GeneratorTask
    )