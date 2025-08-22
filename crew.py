from dotenv import load_dotenv
load_dotenv()

from crewai import Crew
from tasks.generator_task import create_generator_task
from tasks.executor_task import create_executor_task
from agents.generator_agent import GENERATOR_AGENT
from agents.executor_agent import ExecutorAgent

feature_desc = input("Enter feature description: ")

GeneratorTask = create_generator_task(feature_desc)

ExecutorTask = create_executor_task(GeneratorTask)

crew = Crew(
    name="test_crew",
    description="A crew for generating and managing test cases.",
    agents=[
        GENERATOR_AGENT,
        ExecutorAgent
    ],
    tasks=[GeneratorTask, ExecutorTask]
)


if __name__ == "__main__":
    result = crew.kickoff()
    print(result)