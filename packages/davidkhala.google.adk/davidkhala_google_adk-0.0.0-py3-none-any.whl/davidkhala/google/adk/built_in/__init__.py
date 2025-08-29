from google.adk.agents import Agent, BaseAgent
from google.adk.tools import google_search, agent_tool
from google.adk.code_executors import BuiltInCodeExecutor


class ToolAgent(BaseAgent):
    def as_tool(self):
        return agent_tool.AgentTool(agent=self)


class GoogleSearchAgent(Agent, ToolAgent):
    def __init__(self, name, model):
        super().__init__(
            name=name, model=model,
            description="Agent to answer questions using Google Search.",
            instruction="I can answer your questions by searching the internet. Just ask me anything!",
            tools=[google_search]
        )


class CodeExecutionAgent(Agent, ToolAgent):
    def __init__(self, name, model):
        super().__init__(
            name=name, model=model,
            description="Executes Python code to perform calculations.",
            instruction="""You are a calculator agent.
            When given a mathematical expression, write and execute Python code to calculate the result.
            Return only the final numerical result as plain text, without markdown or code blocks.
            """,
            code_executor=BuiltInCodeExecutor(),
        )



