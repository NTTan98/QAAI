from crewai import Task
from agents.generator_agent import GENERATOR_AGENT

GeneratorTask = Task(
    name="generator_task",
    description=(
        "Người dùng cung cấp feature: '{{feature_desc}}'. "
        "Hãy sinh ra JSON test case theo format:\n"
        "[\n"
        "  {\"action\": \"goto\", \"target\": \"https://example.com\"},\n"
        "  {\"action\": \"click\", \"target\": \"#login-btn\"}\n"
        "]"
    ),
    agent=GENERATOR_AGENT,
    expected_output="Json chứa step rõ ràng, có thứ tự hợp lý và dễ chạy tự động."
)
