from crewai import Crew
from tasks.generator_task import GeneratorTask
from tasks.executor_task import ExecutorTask

user_input = """{"steps": [                                                                                                                                                                                                                            
{"action": "goto", "target": "https://www.saucedemo.com/"},                                                                                                                                                                
{"action": "fill", "target": "#user-name", "value": "standard_user"},
{"action": "fill", "target": "#password", "value": "secret_sauce"},
{"action": "click", "target": "#login-button"}
]}"""

ExecutorTask.description = ExecutorTask.description.format(user_input=user_input)

crew = Crew(
    name="test_crew",
    description="A crew for generating and managing test cases.",
    tasks=[ExecutorTask]
)


if __name__ == "__main__":

    result = crew.kickoff()
    print(result)