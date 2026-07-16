from agents import Agent, Runner

from app.services.openai_client import get_async_client

MODEL = "gpt-4o-mini"

# Ensure OPENAI_API_KEY is reachable for the agents SDK, which uses the
# synchronous OpenAI client internally. We pass the key explicitly so that
# environments where only the async client sees the env var still work.
_AGENT_INSTRUCTIONS = "You answer history questions clearly and concisely."


async def run_agent(message: str) -> str:
    """Run the History tutor agent on `message` and return its final output."""
    # Touch the shared client so we fail fast if OPENAI_API_KEY is missing.
    _ = get_async_client()

    agent = Agent(
        name="History tutor",
        instructions=_AGENT_INSTRUCTIONS,
        model=MODEL,
    )
    result = await Runner.run(agent, message)
    return result.final_output