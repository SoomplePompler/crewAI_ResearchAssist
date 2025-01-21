from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from langchain_community.llms import OpenAI, Ollama
from research_assistants.tools.custom_tool import FetchResearchSeleniumInput, FetchResearchSelenium
from crewai_tools import JSONSearchTool, CodeInterpreterTool
import litellm
import os


# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators



@CrewBase
class ResearchAssistants():
	"""ResearchAssistants crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended 
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	llama32 = LLM(
        model="ollama/llama3.2",
    )
	json_search = JSONSearchTool(json_path = '/home/dabe/python3123/research_assistants/json_dump.json', config_path = '/home/dabe/python3123/research_assistants/embedchain_config.yml')
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			llm=self.llama32,
			versbose=True,
			allow_code_execution=False,
			code_execution_mode="safe",  # Uses Docker for safety
			max_execution_time=300,  # 5-minute timeout
			max_retry_limit=3,  # More retries for complex code tasks
			tools=[FetchResearchSelenium()]
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True,
			llm=self.llama32,
			allow_code_execution=False,
			code_execution_mode="safe",  # Uses Docker for safety
			max_execution_time=300,  # 5-minute timeout
			max_retry_limit=3,  # More retries for complex code tasks
			tools = [self.json_search]			
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ResearchAssistants crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
