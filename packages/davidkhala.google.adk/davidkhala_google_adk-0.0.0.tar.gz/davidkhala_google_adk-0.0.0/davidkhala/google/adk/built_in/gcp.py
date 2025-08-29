from google.adk import Agent

from davidkhala.google.adk.built_in import ToolAgent


class BQAgent(Agent, ToolAgent):
    def __init__(self, name, model):
        super().__init__(
            name=name, model=model,
            description="Agent to answer questions about BigQuery data and models and execute SQL queries.",
            instruction="""You are a data science agent with access to several BigQuery tools.
            Make use of those tools to answer the user's questions.
            """,
            tools=[bigquery_toolset],
        )