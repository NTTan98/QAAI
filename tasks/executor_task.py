from crewai import Task
from agents.executor_agent import ExecutorAgent

ExecutorTask = Task(
    description=(
        "Bạn sẽ nhận được một JSON test case từ {user_input}. "
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
)
