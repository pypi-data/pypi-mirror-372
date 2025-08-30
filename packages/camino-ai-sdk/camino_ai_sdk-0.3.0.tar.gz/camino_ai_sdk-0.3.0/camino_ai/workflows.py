"""
Workflow helpers for chaining Camino AI APIs together.

This module provides high-level workflow classes that make it easy to chain
multiple Camino AI endpoints for common use cases like area exploration,
route planning, and POI discovery.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from .client import CaminoAI
from .models import (
    Coordinate, 
    ContextRequest, 
    QueryRequest, 
    JourneyRequest, 
    RelationshipRequest,
    Waypoint,
    TransportMode,
    QueryResult,
    APIError
)


@dataclass
class WorkflowPOI:
    """Enhanced POI with workflow metadata."""
    name: str
    coordinate: Coordinate
    category: str = ""
    address: str = ""
    confidence: float = 0.0
    distance_from_origin: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass 
class WorkflowResult:
    """Result of a workflow execution."""
    success: bool
    total_pois_found: int
    selected_pois: List[WorkflowPOI]
    journey_distance: float = 0.0
    journey_duration: float = 0.0
    error_message: str = ""


class AreaExplorer:
    """
    High-level workflow for exploring an area and planning visits.
    
    This class chains together context → query → journey APIs to:
    1. Discover what's interesting in an area
    2. Get detailed information about POIs
    3. Plan an optimal route through selected POIs
    """
    
    def __init__(self, client: CaminoAI):
        self.client = client
        
    async def explore_and_plan(
        self,
        location: Coordinate,
        poi_types: List[str] = None,
        radius: int = 1000,
        max_pois_per_type: int = 3,
        max_journey_stops: int = 5,
        transport_mode: str = "walking"
    ) -> WorkflowResult:
        """
        Complete workflow: explore area → find POIs → plan journey.
        
        Args:
            location: Starting location coordinate
            poi_types: List of POI types to search for (e.g., ["restaurants", "cafes"])
            radius: Search radius in meters
            max_pois_per_type: Maximum POIs to find per type
            max_journey_stops: Maximum stops in the planned journey
            transport_mode: Transportation mode for journey
            
        Returns:
            WorkflowResult with journey plan and POI details
        """
        try:
            # Step 1: Get area context
            context_info = await self._get_area_context(location, radius)
            
            # Step 2: Determine POI types to search for
            if not poi_types:
                poi_types = self._extract_poi_types_from_context(context_info)
            
            # Step 3: Query for detailed POI information  
            all_pois = await self._query_poi_details(
                location=location,
                poi_types=poi_types, 
                radius=radius,
                max_per_type=max_pois_per_type
            )
            
            if not all_pois:
                return WorkflowResult(
                    success=False,
                    total_pois_found=0,
                    selected_pois=[],
                    error_message="No POIs found in the area"
                )
            
            # Step 4: Select best POIs for journey
            selected_pois = self._select_best_pois(all_pois, max_journey_stops)
            
            # Step 5: Plan optimized journey
            journey_result = await self._plan_journey(
                start_location=location,
                pois=selected_pois,
                transport_mode=transport_mode
            )
            
            return WorkflowResult(
                success=True,
                total_pois_found=len(all_pois),
                selected_pois=selected_pois,
                journey_distance=journey_result.get('distance', 0.0),
                journey_duration=journey_result.get('duration', 0.0)
            )
            
        except Exception as e:
            return WorkflowResult(
                success=False,
                total_pois_found=0,
                selected_pois=[],
                error_message=str(e)
            )
    
    async def _get_area_context(self, location: Coordinate, radius: int) -> Dict[str, Any]:
        """Get contextual information about an area."""
        context_request = ContextRequest(
            location=location,
            radius=f"{radius}m",
            context="Discover interesting places and local information"
        )
        
        try:
            context_response = await self.client.context_async(context_request)
            return {
                'context': getattr(context_response, 'context', {}),
                'nearby': getattr(context_response, 'nearby', [])
            }
        except APIError:
            return {'context': {}, 'nearby': []}
    
    def _extract_poi_types_from_context(self, context_info: Dict[str, Any]) -> List[str]:
        """Extract potential POI types from context information."""
        # This could be enhanced with AI analysis of the context
        # For now, return common useful POI types
        return [
            "restaurants", 
            "cafes", 
            "attractions", 
            "shopping",
            "museums",
            "parks"
        ]
    
    async def _query_poi_details(
        self, 
        location: Coordinate,
        poi_types: List[str],
        radius: int,
        max_per_type: int
    ) -> List[WorkflowPOI]:
        """Query detailed information for each POI type."""
        all_pois = []
        
        for poi_type in poi_types:
            query_request = QueryRequest(
                q=f"{poi_type} near me",
                lat=location.lat,
                lon=location.lon,
                radius=radius,
                limit=max_per_type
            )
            
            try:
                query_response = await self.client.query_async(query_request)
                
                for result in query_response.results:
                    # Calculate distance from start location
                    distance = await self._calculate_distance(location, result.coordinate)
                    
                    workflow_poi = WorkflowPOI(
                        name=result.name,
                        coordinate=result.coordinate,
                        category=result.category or poi_type,
                        address=result.address or "",
                        confidence=result.confidence or 0.0,
                        distance_from_origin=distance,
                        metadata=result.metadata or {}
                    )
                    all_pois.append(workflow_poi)
                    
            except APIError:
                continue  # Skip failed queries
                
        return all_pois
    
    async def _calculate_distance(self, from_loc: Coordinate, to_loc: Coordinate) -> float:
        """Calculate distance between two coordinates."""
        try:
            relationship_request = RelationshipRequest(
                start=from_loc,
                end=to_loc,
                include=["distance"]
            )
            relationship_response = await self.client.relationship_async(relationship_request)
            return relationship_response.total_distance_km * 1000  # Convert to meters
        except APIError:
            return 0.0  # Fallback if distance calculation fails
    
    def _select_best_pois(self, pois: List[WorkflowPOI], max_stops: int) -> List[WorkflowPOI]:
        """Select the best POIs for the journey based on confidence and diversity."""
        # Sort by confidence and proximity (higher confidence, closer is better)
        scored_pois = []
        for poi in pois:
            # Scoring: 70% confidence + 30% proximity (closer = higher score)
            proximity_score = max(0, 1 - (poi.distance_from_origin / 2000))  # Max 2km
            total_score = (poi.confidence * 0.7) + (proximity_score * 0.3)
            scored_pois.append((total_score, poi))
        
        # Sort by score descending
        scored_pois.sort(key=lambda x: x[0], reverse=True)
        
        # Select diverse POIs (prefer different categories)
        selected = []
        used_categories = set()
        
        for score, poi in scored_pois:
            if len(selected) >= max_stops:
                break
                
            # Prefer diversity, but allow same category if score is very high
            if poi.category not in used_categories or score > 0.9:
                selected.append(poi)
                used_categories.add(poi.category)
        
        return selected
    
    async def _plan_journey(
        self, 
        start_location: Coordinate, 
        pois: List[WorkflowPOI],
        transport_mode: str
    ) -> Dict[str, Any]:
        """Plan optimized journey through selected POIs."""
        if not pois:
            return {'distance': 0.0, 'duration': 0.0}
        
        # Create waypoints
        waypoints = [
            Waypoint(location=start_location, purpose="start")
        ]
        
        for poi in pois:
            waypoints.append(
                Waypoint(
                    location=poi.coordinate,
                    purpose=f"visit_{poi.category}"
                )
            )
        
        journey_request = JourneyRequest(
            waypoints=waypoints,
            constraints=JourneyConstraints(
                transport=transport_mode,
                time_budget="4h",
                preferences=["efficient", "safe"]
            )
        )
        
        try:
            journey_response = await self.client.journey_async(journey_request)
            return {
                'distance': journey_response.total_distance,
                'duration': journey_response.total_duration,
                'segments': journey_response.segments
            }
        except APIError:
            return {'distance': 0.0, 'duration': 0.0}


class QuickChain:
    """
    Utility class for quick API chaining operations.
    
    Provides simple methods for common chaining patterns without 
    the full workflow overhead.
    """
    
    def __init__(self, client: CaminoAI):
        self.client = client
    
    async def context_to_query(
        self, 
        location: Coordinate, 
        poi_type: str,
        radius: int = 1000
    ) -> List[QueryResult]:
        """
        Chain context → query: Get area context, then query for specific POIs.
        
        Args:
            location: Location to explore
            poi_type: Type of POI to search for
            radius: Search radius in meters
            
        Returns:
            List of query results for the POI type
        """
        # Get context first (this helps with query refinement)
        try:
            context_request = ContextRequest(
                location=location,
                radius=f"{radius}m"
            )
            await self.client.context_async(context_request)
            # Context provides area understanding for better query results
        except APIError:
            pass  # Continue even if context fails
        
        # Now query for specific POIs with area context
        query_request = QueryRequest(
            q=f"{poi_type} in this area",
            lat=location.lat,
            lon=location.lng,
            radius=radius,
            limit=10
        )
        
        query_response = await self.client.query_async(query_request)
        return query_response.results
    
    async def query_to_journey(
        self,
        start_location: Coordinate,
        query_results: List[QueryResult],
        transport_mode: str = "walking",
        max_stops: int = 4
    ) -> Dict[str, Any]:
        """
        Chain query → journey: Take query results and plan a journey.
        
        Args:
            start_location: Journey starting point
            query_results: Results from a previous query
            transport_mode: How to travel
            max_stops: Maximum number of stops
            
        Returns:
            Journey planning result
        """
        if not query_results:
            raise ValueError("No query results provided for journey planning")
        
        # Select best results (by confidence)
        selected_results = sorted(
            query_results, 
            key=lambda x: x.confidence or 0.0, 
            reverse=True
        )[:max_stops]
        
        # Create waypoints
        waypoints = [Waypoint(location=start_location, purpose="start")]
        
        for result in selected_results:
            waypoints.append(
                Waypoint(
                    location=result.coordinate,
                    purpose=f"visit_{result.category or 'poi'}"
                )
            )
        
        # Plan journey
        journey_request = JourneyRequest(
            waypoints=waypoints,
            constraints=JourneyConstraints(
                transport=transport_mode,
                preferences=["efficient"]
            )
        )
        
        journey_response = await self.client.journey_async(journey_request)
        
        return {
            'total_distance': journey_response.total_distance,
            'total_duration': journey_response.total_duration,
            'stops': len(selected_results),
            'selected_pois': [
                {
                    'name': result.name,
                    'coordinate': {'lat': result.coordinate.lat, 'lon': result.coordinate.lon}
                }
                for result in selected_results
            ],
            'segments': journey_response.segments
        }