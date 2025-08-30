import asyncio
import logging

from rich.logging import RichHandler

from lite_agent.agent import Agent
from lite_agent.runner import Runner

logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("lite_agent")
logger.setLevel(logging.DEBUG)


async def get_temperature(city: str) -> str:
    """Get the temperature for a city."""
    return f"The temperature in {city} is 25°C."


agent = Agent(
    model="gpt-4.1-nano",
    name="Weather Assistant",
    instructions="You are a helpful weather assistant. Before using tools, briefly explain what you are going to do. Provide friendly and informative responses.",
    tools=[get_temperature],
)


async def main():
    runner = Runner(agent, streaming=True, api="responses")
    resp = await runner.run_until_complete(
        "What is the temperature in New York?",
        includes=["usage", "assistant_message", "function_call", "function_call_output", "timing"],
    )
    print(resp[0])


if __name__ == "__main__":
    asyncio.run(main())
