# langchain-camino

[![PyPI version](https://badge.fury.io/py/langchain-camino.svg)](https://badge.fury.io/py/langchain-camino)

An integration package connecting [Camino AI Reality Grounding API](https://getcamino.ai/) and LangChain.

## Installation

```bash
pip install langchain-camino
```

## Setup

To use this package, you need to get a Camino API key from [https://app.getcamino.ai/](https://app.getcamino.ai/).

```bash
export CAMINO_API_KEY="your-api-key"
```

## Usage

### CaminoSearch - Place Search

Search for places by name using Nominatim:

```python
from langchain_camino import CaminoSearch

# Initialize the tool
search = CaminoSearch()

# Search for places
result = search.invoke({"place_name": "coffee shops in San Francisco"})
print(result)
```

### CaminoQuery - Natural Language Location Queries

Make natural language location queries with optional AI ranking:

```python
from langchain_camino import CaminoQuery

# Initialize the tool
query = CaminoQuery(ai_ranking=True)

# Query with natural language
result = query.invoke({
    "query": "Find good restaurants near me",
    "lat": 37.7749,
    "lon": -122.4194,
    "radius": 1.0
})
print(result)
```

### CaminoJourney - Multi-waypoint Journey Planning

Plan optimized journeys with multiple stops:

```python
from langchain_camino import CaminoJourney

# Initialize the tool
journey = CaminoJourney(transport_mode="car", optimize=True)

# Plan a journey
waypoints = [
    (37.7749, -122.4194),  # San Francisco
    (37.7849, -122.4094),  # Next stop
    (37.7949, -122.3994)   # Final destination
]

result = journey.invoke({
    "waypoints": waypoints,
    "transport_mode": "car",
    "optimize": True
})
print(result)
```

## Using with LangChain Agents

All tools can be used with LangChain agents:

```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_camino import CaminoSearch, CaminoQuery, CaminoJourney

# Initialize LLM
llm = ChatOpenAI(temperature=0)

# Initialize tools
tools = [
    CaminoSearch(),
    CaminoQuery(), 
    CaminoJourney()
]

# Create agent
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use the agent
response = agent.run("Find a coffee shop in downtown San Francisco and plan a route there from the Golden Gate Bridge")
```

## API Reference

### CaminoSearch

Search for places by name using the Camino API.

**Parameters:**
- `place_name` (str): Name of the place to search for
- `limit` (int, optional): Maximum number of results (default: 5)

### CaminoQuery

Make natural language location queries.

**Parameters:**
- `query` (str): Natural language query
- `lat` (float, optional): Latitude for location context
- `lon` (float, optional): Longitude for location context  
- `radius` (float, optional): Search radius in kilometers
- `limit` (int, optional): Maximum number of results (default: 10)
- `ai_ranking` (bool, optional): Use AI-powered ranking (default: True)

### CaminoJourney

Plan multi-waypoint journeys with route optimization.

**Parameters:**
- `waypoints` (List[Tuple[float, float]]): List of (lat, lon) coordinates
- `transport_mode` (str, optional): Transport mode - "car", "bike", "foot", "transit" (default: "car")
- `optimize` (bool, optional): Optimize route for time/distance (default: True)

## Development

### Setup

```bash
git clone https://github.com/your-repo/langchain-camino
cd langchain-camino
pip install -e ".[test,lint]"
```

### Testing

```bash
# Run unit tests
pytest tests/unit_tests/

# Run integration tests (requires API key)
pytest tests/integration_tests/

# Run all tests
pytest
```

### Linting

```bash
# Run linting
ruff check .

# Run type checking
mypy langchain_camino/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.