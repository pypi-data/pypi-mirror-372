import os
from typing import Literal

from tavily import TavilyClient
from camino_ai import CaminoAI, APIError


from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
camino_client = CaminoAI(api_key=os.environ.get("CAMINO_API_KEY"))

# Search tool to use to do research
def location_query(
    query: str,
    max_results: int = 5
):
    """run a location query to understand broad questions about an area"""
    return camino_client.query(
        query
    )

# Search tool to use to do research
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# Prompt prefix to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.

You have access to a few tools.

## `internet_search`
## `location_query`

Use this to run an location-based search for a given query.
"""

# Create the agent
agent = create_deep_agent(
    [location_query],
    research_instructions,
)

# Invoke the agent
result = agent.invoke({"messages": [{"role": "user", "content": "what are the best coffee shops in Paris?"}]})
print(result)