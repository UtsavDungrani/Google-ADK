import os
import asyncio
import warnings
import logging
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

os.environ.setdefault("GOOGLE_GENAI_USE_ENTERPRISE", "False")

# Default to native Gemini model (or LiteLlm if external provider keys have credits)
MODEL_NAME = os.environ.get("DEFAULT_MODEL", "gemini-3.1-flash-lite")

MODEL_GREETER     = MODEL_NAME
MODEL_FAREWELL    = MODEL_NAME
MODEL_WEATHER     = MODEL_NAME
MODEL_COORDINATOR = MODEL_NAME

def get_weather(city: str, context: ToolContext) -> dict:
    """Retrieves the current weather report for a specified city and stores it in session state.
    Args:
        city (str): The name of the city (e.g., 'New York', 'London', 'Tokyo').
    Returns:
        dict: Weather report data or error message.
    """
    print(f"--- [Tool Triggered] Fetching weather for: {city} ---")
    
    context.state["last_city"] = city

    mock_db = {
        "newyork": {"status": "success", "report": "Sunny, 25°C in New York."},
        "london": {"status": "success", "report": "Cloudy, 15°C in London."},
        "tokyo": {"status": "success", "report": "Light rain, 18°C in Tokyo."},
    }
    
    normalized = city.lower().replace(" ", "")
    return mock_db.get(
        normalized, 
        {"status": "error", "error_message": f"Sorry, no data found for '{city}'."}
    )

def input_guardrail(callback_context, llm_request: LlmRequest):
    """Blocks restricted queries before sending them to the LLM."""
    for content in (llm_request.contents or []):
        for part in (content.parts or []):
            if part.text and "restricted_topic" in part.text.lower():
                return LlmResponse(
                    content=types.Content(
                        role="model",
                        parts=[types.Part.from_text(text="I cannot discuss restricted topics per safety policy.")]
                    )
                )
    return None

def tool_guardrail(tool: BaseTool, args: dict, tool_context: ToolContext):
    """Sanitizes arguments before executing any tool."""
    if tool.name == "get_weather":
        city = args.get("city", "")
        if any(char in city for char in ["<", ">", ";", "$", "{", "}"]):
            raise ValueError("Malicious characters detected in city name.")
    return None

greeter_agent = Agent(
    name="greeter",
    model=MODEL_GREETER,
    instruction="You specialize in warm greetings and asking how to help.",
    before_model_callback=input_guardrail,
)

farewell_agent = Agent(
    name="farewell",
    model=MODEL_FAREWELL,
    instruction="You specialize in polite goodbyes and closing conversations.",
    before_model_callback=input_guardrail,
)

weather_specialist = Agent(
    name="weather_specialist",
    model=MODEL_WEATHER,
    instruction="Answer weather queries accurately. Always use the `get_weather` tool when a city is provided.",
    tools=[get_weather],
    before_tool_callback=tool_guardrail,
    before_model_callback=input_guardrail,
)

root_agent = Agent(
    name="coordinator_agent",
    model=MODEL_COORDINATOR,
    instruction=(
        "You coordinate user requests to the appropriate team member: "
        "delegate greetings to 'greeter', fare-thee-wells to 'farewell', "
        "and weather inquiries to 'weather_specialist'."
    ),
    sub_agents=[greeter_agent, farewell_agent, weather_specialist],
    before_model_callback=input_guardrail,
)

async def main():
    app_name = "agents_team"
    user_id = "demo_user"
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=app_name, user_id=user_id)
    runner = Runner(agent=root_agent, session_service=session_service, app_name=app_name)

    test_queries = [
        "Hi there, how are you doing today?",
        "Can you check what the weather is like in London?",
        "Thanks for the info, goodbye!"
    ]

    for query in test_queries:
        print(f"\n[User]: {query}")
        user_content = types.Content(
            role="user", 
            parts=[types.Part.from_text(text=query)]
        )
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=user_content
        ):
            if event.message and event.message.parts:
                for part in event.message.parts:
                    if part.text:
                        print(f"[{event.node_name or 'Agent'}]: {part.text}")
        await asyncio.sleep(2)  # Pause between queries to respect free-tier rate limits

if __name__ == "__main__":
    asyncio.run(main())