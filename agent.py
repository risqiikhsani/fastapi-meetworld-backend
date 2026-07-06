
import asyncio

from agents import Agent, Runner

agent = Agent(
    name="History tutor",
    instructions="You answer history questions clearly and concisely.",
    model="gpt-5.5",
)


async def main() -> None:
    result = await Runner.run(agent, "When did the Roman Empire fall?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
