"""Data models for the Camino AI SDK."""

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class Coordinate(BaseModel):
    """Geographic coordinate with latitude and longitude."""

    lat: float = Field(...,
                       description="Latitude in decimal degrees", ge=-90, le=90)
    lon: float = Field(...,
                       description="Longitude in decimal degrees", ge=-180, le=180)

    @property
    def lng(self) -> float:
        """Alias for lon for backward compatibility."""
        return self.lon


class TransportMode(str, Enum):
    """Available transport modes for routing."""

    DRIVING = "driving"
    WALKING = "walking"
    CYCLING = "cycling"
    TRANSIT = "transit"


class QueryRequest(BaseModel):
    """Request model for natural language location queries."""

    query: str = Field(...,
                       description="Natural language query, e.g., 'coffee near me'")
    lat: Optional[float] = Field(
        None, description="Latitude for the center of your search")
    lon: Optional[float] = Field(
        None, description="Longitude for the center of your search")
    radius: Optional[int] = Field(
        None, description="Search radius in meters. Only used if lat/lon are provided.")
    rank: Optional[bool] = Field(
        True, description="Use AI to rank results by relevance (default: true)")
    limit: Optional[int] = Field(
        20, description="Maximum number of results to return (1-100, default: 20)", ge=1, le=100)
    offset: Optional[int] = Field(
        0, description="Number of results to skip for pagination (default: 0)", ge=0)
    answer: Optional[bool] = Field(
        False, description="Generate a human-readable answer summary (default: false)")


class QueryResult(BaseModel):
    """Individual result from a query."""

    id: int = Field(..., description="Unique identifier for the location")
    type: str = Field(..., description="OSM type (node, way, relation)")
    location: Coordinate = Field(..., description="Geographic coordinates")
    tags: Dict[str, Any] = Field(..., description="OSM tags for the location")
    name: str = Field(..., description="Name of the location")
    amenity: Optional[str] = Field(None, description="Type of amenity")
    cuisine: Optional[str] = Field(
        None, description="Cuisine type if applicable")
    relevance_rank: int = Field(..., description="AI relevance ranking")

    @property
    def coordinate(self) -> Coordinate:
        """Alias for location field for backward compatibility."""
        return self.location

    @property
    def category(self) -> Optional[str]:
        """Extract category from amenity or cuisine for backward compatibility."""
        return self.amenity or self.cuisine

    @property
    def address(self) -> Optional[str]:
        """Extract address from tags if available."""
        # Try to construct address from various tag fields
        addr_parts = []
        if 'addr:housenumber' in self.tags:
            addr_parts.append(self.tags['addr:housenumber'])
        if 'addr:street' in self.tags:
            addr_parts.append(self.tags['addr:street'])
        if 'addr:city' in self.tags:
            addr_parts.append(self.tags['addr:city'])
        return ' '.join(addr_parts) if addr_parts else None

    @property
    def confidence(self) -> float:
        """Calculate confidence score based on relevance rank."""
        # Convert relevance rank to confidence score (rank 1 = 1.0, rank 10 = 0.1)
        return max(0.1, 1.0 - (self.relevance_rank - 1) * 0.1)

    @property
    def metadata(self) -> Dict[str, Any]:
        """Return tags as metadata."""
        return self.tags


class Pagination(BaseModel):
    """Pagination information for query results."""

    total_results: int = Field(...,
                               description="Total number of results available")
    limit: int = Field(..., description="Maximum results per page")
    offset: int = Field(..., description="Current offset")
    returned_count: int = Field(...,
                                description="Number of results in this response")
    has_more: bool = Field(...,
                           description="Whether more results are available")
    next_offset: Optional[int] = Field(
        None, description="Offset for next page")


class QueryResponse(BaseModel):
    """Response model for location queries."""

    query: str = Field(..., description="The original query string")
    results: List[QueryResult] = Field(..., description="Query results")
    ai_ranked: bool = Field(..., description="Whether results were AI-ranked")
    pagination: Pagination = Field(..., description="Pagination information")
    answer: Optional[str] = Field(
        None, description="AI-generated answer summary")

    @property
    def total(self) -> int:
        """Alias for pagination.total_results for backward compatibility."""
        return self.pagination.total_results


class RelationshipRequest(BaseModel):
    """Request model for spatial relationship queries."""

    start: Coordinate = Field(..., description="Starting location")
    end: Coordinate = Field(..., description="Target location")
    include: Optional[List[str]] = Field(
        default=["distance", "direction", "travel_time", "description"],
        description="List of relationship aspects to include in response"
    )


class LocationWithPurpose(BaseModel):
    """Location with purpose information."""

    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    purpose: str = Field(..., description="Purpose of this location")


class RouteSegmentInfo(BaseModel):
    """Route segment in relationship response."""

    from_: LocationWithPurpose = Field(...,
                                       alias="from", description="Starting point")
    to: LocationWithPurpose = Field(..., description="Ending point")
    distance_km: float = Field(..., description="Distance in kilometers")
    estimated_time: str = Field(...,
                                description="Estimated time as formatted string")

    model_config = {"populate_by_name": True}


class RelationshipAnalysis(BaseModel):
    """Analysis section of relationship response."""

    summary: str = Field(..., description="Summary of the route analysis")
    optimization_opportunities: List[str] = Field(
        ..., description="List of optimization suggestions")


class RelationshipResponse(BaseModel):
    """Response model for spatial relationships."""

    distance: str = Field(..., description="Formatted distance string")
    direction: str = Field(..., description="Direction from start to end")
    walking_time: str = Field(..., description="Formatted walking time")
    actual_distance_km: float = Field(...,
                                      description="Actual distance in kilometers")
    duration_seconds: float = Field(..., description="Duration in seconds")
    driving_time: str = Field(..., description="Formatted driving time")
    description: str = Field(..., description="Human-readable description")


class ContextRequest(BaseModel):
    """Request model for location context."""

    location: Coordinate = Field(...,
                                 description="Location to get context for")
    radius: Optional[int] = Field(
        None, description="Context radius in meters (e.g., 500, 1000)")
    context: Optional[str] = Field(
        None, description="Context description for what to find")
    categories: Optional[List[str]] = Field(
        None, description="Specific categories to include")


class RelevantPlaces(BaseModel):
    """Categorized relevant places in the context area."""

    restaurants: List[str] = Field(..., description="Restaurant names")
    services: List[str] = Field(..., description="Service establishment names")
    shops: List[str] = Field(..., description="Shop names")
    attractions: List[str] = Field(..., description="Attraction names")


class ContextResponse(BaseModel):
    """Response model for location context."""

    area_description: str = Field(..., description="Description of the area")
    relevant_places: RelevantPlaces = Field(...,
                                            description="Categorized places in the area")
    location: Coordinate = Field(..., description="Queried location")
    search_radius: int = Field(..., description="Search radius used in meters")
    total_places_found: int = Field(...,
                                    description="Total number of places found")


class Waypoint(BaseModel):
    """Waypoint for journey planning."""

    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    purpose: str = Field(..., description="Purpose of this waypoint")


class JourneyRequest(BaseModel):
    """Request model for multi-waypoint journey planning."""

    waypoints: List[Waypoint] = Field(..., description="Journey waypoints")
    constraints: Optional[Dict[str, Any]] = Field(
        None, description="Journey constraints like transport mode and time budget")


class RouteSegment(BaseModel):
    """Individual route segment for backward compatibility."""

    start: Coordinate = Field(..., description="Segment start coordinate")
    end: Coordinate = Field(..., description="Segment end coordinate")
    distance: float = Field(..., description="Segment distance in meters")
    duration: float = Field(..., description="Segment duration in seconds")
    instructions: Optional[str] = Field(
        None, description="Turn-by-turn instructions")


class JourneyResponse(BaseModel):
    """Response model for journey planning."""

    feasible: bool = Field(..., description="Whether the journey is feasible")
    total_distance_km: float = Field(...,
                                     description="Total journey distance in kilometers")
    total_time_minutes: int = Field(...,
                                    description="Total journey time in minutes")
    total_time_formatted: str = Field(...,
                                      description="Formatted total time string")
    transport_mode: str = Field(..., description="Transport mode used")
    route_segments: List[RouteSegmentInfo] = Field(
        ..., description="Journey route segments")
    analysis: RelationshipAnalysis = Field(...,
                                           description="Route analysis and optimization")


class RouteRequest(BaseModel):
    """Request model for point-to-point routing."""

    start_lat: float = Field(..., description="Starting latitude")
    start_lon: float = Field(..., description="Starting longitude")
    end_lat: float = Field(..., description="Ending latitude")
    end_lon: float = Field(..., description="Ending longitude")
    mode: Optional[str] = Field(
        "foot", description="Transport mode (foot, car, bicycle)")
    include_geometry: Optional[bool] = Field(
        True, description="Include route geometry")


class RouteSummary(BaseModel):
    """Summary information for a route."""

    total_distance_meters: float = Field(...,
                                         description="Total distance in meters")
    total_duration_seconds: float = Field(...,
                                          description="Total duration in seconds")


class RouteResponse(BaseModel):
    """Response model for routing."""

    summary: RouteSummary = Field(..., description="Route summary")
    instructions: List[str] = Field(...,
                                    description="Turn-by-turn instructions")
    geometry: Optional[Dict[str, Any]] = Field(
        None, description="Route geometry data")
    include_geometry: bool = Field(...,
                                   description="Whether geometry was included")


# Exception classes
class CaminoError(Exception):
    """Base exception for Camino AI SDK."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class APIError(CaminoError):
    """API-related error."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, response)
        self.status_code = status_code
        self.response = response


class AuthenticationError(APIError):
    """Authentication failed."""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after
