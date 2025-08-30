# Camino AI Python SDK

The official Python SDK for [Camino AI](https://getcamino.ai) - Guide your AI agents through the real world with location intelligence, spatial reasoning, and route planning.

## Features

- 🌍 **Natural Language Queries**: Search for places using natural language
- 📍 **Spatial Relationships**: Calculate distances, bearings, and spatial relationships
- 🗺️ **Location Context**: Get rich contextual information about any location
- 🧭 **Journey Planning**: Multi-waypoint journey optimization
- 🛤️ **Routing**: Point-to-point routing with multiple transport modes
- ⚡ **Async Support**: Full async/await support for all operations
- 🔄 **Auto Retry**: Built-in retry logic with exponential backoff
- 📝 **Type Hints**: Full type annotations for better IDE support
- 🛡️ **Error Handling**: Comprehensive error handling with custom exceptions

## Installation

```bash
pip install camino-ai-sdk
```

## Quick Start

```python
from camino_ai import CaminoAI

# Initialize the client
client = CaminoAI(api_key="your-api-key")

# Search for coffee shops
response = client.query("coffee shops near Central Park")
for result in response.results:
    print(f"{result.name}: {result.address}")

# Calculate spatial relationship
from camino_ai import RelationshipRequest, Coordinate

relationship = client.relationship(RelationshipRequest(
    from_location=Coordinate(lat=40.7831, lng=-73.9712),  # Central Park
    to_location=Coordinate(lat=40.7589, lng=-73.9851)     # Times Square
))
print(f"Distance: {relationship.distance}m")
```

## Async Usage

```python
import asyncio
from camino_ai import CaminoAI

async def main():
    async with CaminoAI(api_key="your-api-key") as client:
        response = await client.query_async("restaurants in Brooklyn")
        print(f"Found {len(response.results)} restaurants")

asyncio.run(main())
```

## API Reference

### Client Initialization

```python
client = CaminoAI(
    api_key="your-api-key",
    base_url="https://api.getcamino.ai",  # Optional
    timeout=30.0,                        # Optional
    max_retries=3,                       # Optional
    retry_backoff=1.0                    # Optional
)
```

### Query

Search for points of interest using natural language:

```python
# Simple string query
response = client.query("pizza places in Manhattan")

# Advanced query with parameters
from camino_ai import QueryRequest, Coordinate

request = QueryRequest(
    query="coffee shops",
    location=Coordinate(lat=40.7831, lng=-73.9712),
    radius=1000,  # meters
    limit=10
)
response = client.query(request)
```

### Relationships

Calculate spatial relationships between locations:

```python
from camino_ai import RelationshipRequest, Coordinate

request = RelationshipRequest(
    from_location=Coordinate(lat=40.7831, lng=-73.9712),
    to_location=Coordinate(lat=40.7589, lng=-73.9851),
    relationship_type="distance_and_bearing"
)
response = client.relationship(request)
print(f"Distance: {response.distance}m, Bearing: {response.bearing}°")
```

### Context

Get contextual information about a location:

```python
from camino_ai import ContextRequest, Coordinate

request = ContextRequest(
    location=Coordinate(lat=40.7831, lng=-73.9712),
    radius=500,
    categories=["restaurant", "entertainment"]
)
response = client.context(request)
print(f"Context: {response.context}")
```

### Journey Planning

Plan optimized multi-waypoint journeys:

```python
from camino_ai import JourneyRequest, Waypoint, JourneyConstraints, TransportMode

request = JourneyRequest(
    waypoints=[
        Waypoint(location=Coordinate(lat=40.7831, lng=-73.9712)),
        Waypoint(location=Coordinate(lat=40.7589, lng=-73.9851)),
        Waypoint(location=Coordinate(lat=40.7505, lng=-73.9934))
    ],
    constraints=JourneyConstraints(
        transport_mode=TransportMode.DRIVING,
        avoid_tolls=True
    ),
    optimize=True
)
response = client.journey(request)
print(f"Total distance: {response.total_distance}m")
print(f"Total duration: {response.total_duration}s")
```

### Routing

Calculate routes between two points:

```python
from camino_ai import RouteRequest, Coordinate, TransportMode

request = RouteRequest(
    start=Coordinate(lat=40.7831, lng=-73.9712),
    end=Coordinate(lat=40.7589, lng=-73.9851),
    transport_mode=TransportMode.WALKING,
    avoid_highways=True
)
response = client.route(request)
print(f"Route distance: {response.distance}m")
print(f"Route duration: {response.duration}s")
```

## Error Handling

The SDK provides specific exception types for different error conditions:

```python
from camino_ai import CaminoAI, APIError, AuthenticationError, RateLimitError

try:
    client = CaminoAI(api_key="invalid-key")
    response = client.query("coffee shops")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after}s")
except APIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

## Transport Modes

Available transport modes for routing and journey planning:

- `TransportMode.DRIVING` - Car/driving directions
- `TransportMode.WALKING` - Walking directions  
- `TransportMode.CYCLING` - Bicycle directions
- `TransportMode.TRANSIT` - Public transportation

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/camino-ai/camino-sdks.git
cd camino-sdks/python

# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=camino_ai

# Run type checking
poetry run mypy camino_ai
```

### Formatting

```bash
# Format code
poetry run black camino_ai tests
poetry run isort camino_ai tests

# Lint code
poetry run flake8 camino_ai tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Support

- 📧 Email: support@getcamino.ai
- 🐛 Issues: [GitHub Issues](https://github.com/camino-ai/camino-sdks/issues)
- 📖 Documentation: [docs.getcamino.ai](https://docs.getcamino.ai)