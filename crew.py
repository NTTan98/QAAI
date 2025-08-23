from dotenv import load_dotenv
load_dotenv()

from crewai import Crew
from tasks.generator_task import create_generator_task
from tasks.executor_task import create_executor_task
from tasks.decision_task  import create_decision_task
from agents.generator_agent import GENERATOR_AGENT
from agents.executor_agent import ExecutorAgent
from agents.multi_agent import MultiAgent


# feature_desc = input("Enter feature description: ")
feature_desc = "vào trang https://www.saucedemo.com/ và đăng nhập bằng account: standard_user và pass secret_sauce"

GeneratorTask = create_generator_task(feature_desc)

ExecutorTask = create_executor_task(GeneratorTask)

DecisionTask = create_decision_task(ExecutorTask, GeneratorTask)

crew = Crew(
    name="test_crew",
    description="A crew for generating and managing test cases.",
    agents=[
        GENERATOR_AGENT,
        ExecutorAgent,
        MultiAgent
    ],
    tasks=[GeneratorTask, ExecutorTask, DecisionTask]
)


if __name__ == "__main__":
    result = crew.kickoff()
    print("Final Decision Task Result:")
    print(result)