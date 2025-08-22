from crewai import Task
from agents.generator_agent import GENERATOR_AGENT


def create_generator_task(feature_desc: str) -> Task:
    """Return a Task configured to generate JSON test cases for the given feature description."""
    return Task(
        name="generator_task",
        description=(
            f"Người dùng cung cấp feature: '{feature_desc}'. "
            "Hãy sinh ra string JSON test case theo format:\n"
            "{steps: [\n"
            "  {\"action\": \"goto\", \"target\": \"https://example.com\"},\n"
            "  {\"action\": \"click\", \"target\": \"#login-btn\"}\n"
            "]"
        ),
        agent=GENERATOR_AGENT,
        expected_output=(
            "Json chứa step rõ ràng, có thứ tự hợp lý và dễ chạy tự động."
        ),
    )
