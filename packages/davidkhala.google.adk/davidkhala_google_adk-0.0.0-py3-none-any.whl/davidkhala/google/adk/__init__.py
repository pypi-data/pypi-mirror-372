from typing import Optional, Any, Coroutine

from google.adk.agents import BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


class AsyncSession:
    def __init__(self, agent: BaseAgent, user_id: str, app_name: Optional[str] = None):
        if app_name is None:
            app_name = agent.name # assume agent is root_agent
        self.app_name = app_name  # unique id for entire adk app.
        self.user_id = user_id
        self.agent = agent

    # Session and Runner
    async def setup_session_and_runner(self):
        session_service = InMemorySessionService()
        session = await session_service.create_session(app_name=self.app_name, user_id=self.user_id)
        runner = Runner(agent=self.agent, app_name=self.app_name, session_service=session_service)
        return session, runner

    # Agent Interaction
    async def call_agent_async(self, query: str) -> str:
        content = types.Content(role='user', parts=[types.Part(text=query)])
        session, runner = await self.setup_session_and_runner()
        events = runner.run_async(user_id=self.user_id, session_id=session.id, new_message=content)

        async for event in events:
            if event.is_final_response():
                return event.content.parts[0].text
        assert False
