"""SDK wrapper for Camino AI integration with LangChain.

This module provides a wrapper around the official camino-ai-sdk
to maintain compatibility with our LangChain tools.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, SecretStr, model_validator

from camino_ai import (
    CaminoAI,
    QueryRequest,
    RelationshipRequest,
    ContextRequest,
    JourneyRequest,
    RouteRequest,
    Coordinate,
    Waypoint,
    TransportMode,
    APIError,
)


class CaminoSDKWrapper(BaseModel):
    """Wrapper for Camino AI SDK."""

    camino_api_key: SecretStr
    base_url: Optional[str] = None
    _client: Optional[CaminoAI] = None

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        """Validate that api key exists in environment."""
        camino_api_key = get_from_dict_or_env(
            values, "camino_api_key", "CAMINO_API_KEY"
        )
        values["camino_api_key"] = camino_api_key
        return values

    def _get_client(self) -> CaminoAI:
        """Get or create the Camino AI client."""
        if self._client is None:
            # Only pass base_url if it's explicitly set
            kwargs = {"api_key": self.camino_api_key.get_secret_value()}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = CaminoAI(**kwargs)
        return self._client

    def search_places(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search for places using simple query."""
        try:
            client = self._get_client()
            # Use QueryRequest explicitly to ensure correct field names  
            request = QueryRequest(query=query, limit=limit)
            response = client.query(request)
            
            # Convert SDK response to expected format with safe attribute access
            places = []
            for result in (response.results[:limit] if limit else response.results):
                # Coordinates are in result.location.lat/lon
                location = getattr(result, "location", None)
                lat = location.lat if location else None
                lon = location.lon if location else None
                
                place = {
                    "name": getattr(result, "name", ""),
                    "lat": lat,
                    "lon": lon,
                    "address": getattr(result, "address", None) or "",
                    "place_type": getattr(result, "category", None) or ""
                }
                places.append(place)
            
            return {
                "places": places,
                "query": query,
                "total_results": response.total
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    async def search_places_async(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search for places using simple query (async)."""
        try:
            client = self._get_client()
            response = await client.query_async(q)
            
            # Convert SDK response to expected format
            return {
                "places": [
                    {
                        "name": result.name,
                        "lat": result.lat,
                        "lon": result.lon,
                        "address": getattr(result, "address", ""),
                        "place_type": getattr(result, "category", "")
                    }
                    for result in (response.results[:limit] if limit else response.results)
                ],
                "query": query,
                "total_results": response.total
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    def query_locations(
        self,
        query: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[float] = None,
        limit: Optional[int] = None,
        rank: Optional[bool] = None,
        offset: Optional[int] = None,
        answer: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Make natural language location queries."""
        try:
            client = self._get_client()
            
            # Create request object if we have location parameters
            if any([lat, lon, radius, limit, offset, answer]):
                request = QueryRequest(
                    query=query,
                    lat=lat,
                    lon=lon,
                    radius=radius,
                    limit=limit or 20,
                    offset=offset or 0
                )
                response = client.query(request)
            else:
                response = client.query(query)
            
            # Convert SDK response to expected format
            return {
                "results": [
                    {
                        "name": getattr(result, "name", ""),
                        "lat": getattr(result, "location", None).lat if getattr(result, "location", None) else None,
                        "lon": getattr(result, "location", None).lon if getattr(result, "location", None) else None,
                        "distance": getattr(result, "distance", None),
                        "type": getattr(result, "category", "") or "",
                        "rating": getattr(result, "rating", None),
                        "confidence": getattr(result, "confidence", None)
                    }
                    for result in response.results
                ],
                "query": query,
                "total_results": response.total,
                "ai_ranked": rank if rank is not None else True
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    async def query_locations_async(
        self,
        query: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[float] = None,
        limit: Optional[int] = None,
        rank: Optional[bool] = None,
        offset: Optional[int] = None,
        answer: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Make natural language location queries (async)."""
        try:
            client = self._get_client()
            
            # Create request object if we have location parameters
            if any([lat, lon, radius, limit, offset, answer]):
                request = QueryRequest(
                    query=query,
                    lat=lat,
                    lon=lon,
                    radius=radius,
                    limit=limit or 20,
                    offset=offset or 0
                )
                response = await client.query_async(request)
            else:
                response = await client.query_async(query)
            
            # Convert SDK response to expected format
            return {
                "results": [
                    {
                        "name": getattr(result, "name", ""),
                        "lat": getattr(result, "location", None).lat if getattr(result, "location", None) else None,
                        "lon": getattr(result, "location", None).lon if getattr(result, "location", None) else None,
                        "distance": getattr(result, "distance", None),
                        "type": getattr(result, "category", "") or "",
                        "rating": getattr(result, "rating", None),
                        "confidence": getattr(result, "confidence", None)
                    }
                    for result in response.results
                ],
                "query": query,
                "total_results": response.total,
                "ai_ranked": rank if rank is not None else True
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    def plan_journey(
        self,
        waypoints: List[Tuple[float, float]],
        transport_mode: Optional[str] = None,
        optimize: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Plan multi-waypoint journeys."""
        try:
            client = self._get_client()
            
            # Convert waypoints to SDK format
            sdk_waypoints = [
                Waypoint(lat=lat, lon=lon, purpose=f"Stop {i+1}")
                for i, (lat, lon) in enumerate(waypoints)
            ]
            
            # Create journey request
            constraints = {}
            if transport_mode:
                constraints["transport"] = transport_mode
            
            request = JourneyRequest(
                waypoints=sdk_waypoints,
                constraints=constraints
            )
            
            response = client.journey(request)
            
            # Convert SDK response to expected format
            return {
                "journey": {
                    "total_distance": response.total_distance_km,
                    "total_duration": getattr(response, "total_time_seconds", None),
                    "optimized": optimize if optimize is not None else True,
                    "transport_mode": response.transport_mode,
                    "feasible": response.feasible,
                    "waypoints": [
                        {
                            "lat": wp.lat,
                            "lon": wp.lon,
                            "order": i,
                            "purpose": wp.purpose
                        }
                        for i, wp in enumerate(sdk_waypoints)
                    ],
                    "route_geometry": getattr(response, "geometry", ""),
                    "instructions": getattr(response, "instructions", [])
                }
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    async def plan_journey_async(
        self,
        waypoints: List[Tuple[float, float]],
        transport_mode: Optional[str] = None,
        optimize: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Plan multi-waypoint journeys (async)."""
        try:
            client = self._get_client()
            
            # Convert waypoints to SDK format
            sdk_waypoints = [
                Waypoint(lat=lat, lon=lon, purpose=f"Stop {i+1}")
                for i, (lat, lon) in enumerate(waypoints)
            ]
            
            # Create journey request
            constraints = {}
            if transport_mode:
                constraints["transport"] = transport_mode
            
            request = JourneyRequest(
                waypoints=sdk_waypoints,
                constraints=constraints
            )
            
            response = await client.journey_async(request)
            
            # Convert SDK response to expected format
            return {
                "journey": {
                    "total_distance": response.total_distance_km,
                    "total_duration": getattr(response, "total_time_seconds", None),
                    "optimized": optimize if optimize is not None else True,
                    "transport_mode": response.transport_mode,
                    "feasible": response.feasible,
                    "waypoints": [
                        {
                            "lat": wp.lat,
                            "lon": wp.lon,
                            "order": i,
                            "purpose": wp.purpose
                        }
                        for i, wp in enumerate(sdk_waypoints)
                    ],
                    "route_geometry": getattr(response, "geometry", ""),
                    "instructions": getattr(response, "instructions", [])
                }
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    def get_spatial_relationship(
        self,
        location1: Tuple[float, float],
        location2: Tuple[float, float],
        include_travel_time: Optional[bool] = None,
        transport_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate spatial relationships between locations."""
        try:
            client = self._get_client()
            
            request = RelationshipRequest(
                start=Coordinate(lat=location1[0], lon=location1[1]),
                end=Coordinate(lat=location2[0], lon=location2[1]),
                include=["distance", "direction", "travel_time", "description"]
            )
            
            response = client.relationship(request)
            
            return {
                "distance": response.distance,
                "distance_km": response.actual_distance_km,
                "direction": response.direction,
                "walking_time": response.walking_time,
                "driving_time": response.driving_time,
                "description": response.description
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    async def get_spatial_relationship_async(
        self,
        location1: Tuple[float, float],
        location2: Tuple[float, float],
        include_travel_time: Optional[bool] = None,
        transport_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate spatial relationships between locations (async)."""
        try:
            client = self._get_client()
            
            request = RelationshipRequest(
                start=Coordinate(lat=location1[0], lon=location1[1]),
                end=Coordinate(lat=location2[0], lon=location2[1]),
                include=["distance", "direction", "travel_time", "description"]
            )
            
            response = await client.relationship_async(request)
            
            return {
                "distance": response.distance,
                "distance_km": response.actual_distance_km,
                "direction": response.direction,
                "walking_time": response.walking_time,
                "driving_time": response.driving_time,
                "description": response.description
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    def get_location_context(
        self,
        lat: float,
        lon: float,
        radius: Optional[float] = None,
        include_accessibility: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get contextual information about a location."""
        try:
            client = self._get_client()
            
            request = ContextRequest(
                location=Coordinate(lat=lat, lon=lon),
                radius=radius or 500,
                categories=["restaurant", "entertainment", "shopping", "services"]
            )
            
            response = client.context(request)
            
            return {
                "area_description": response.area_description,
                "search_radius": response.search_radius,
                "total_places_found": response.total_places_found,
                "relevant_places": {
                    "restaurants": response.relevant_places.restaurants,
                    "services": response.relevant_places.services,
                    "shops": response.relevant_places.shops,
                    "attractions": response.relevant_places.attractions
                }
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    async def get_location_context_async(
        self,
        lat: float,
        lon: float,
        radius: Optional[float] = None,
        include_accessibility: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get contextual information about a location (async)."""
        try:
            client = self._get_client()
            
            request = ContextRequest(
                location=Coordinate(lat=lat, lon=lon),
                radius=radius or 500,
                categories=["restaurant", "entertainment", "shopping", "services"]
            )
            
            response = await client.context_async(request)
            
            return {
                "area_description": response.area_description,
                "search_radius": response.search_radius,
                "total_places_found": response.total_places_found,
                "relevant_places": {
                    "restaurants": response.relevant_places.restaurants,
                    "services": response.relevant_places.services,
                    "shops": response.relevant_places.shops,
                    "attractions": response.relevant_places.attractions
                }
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    def get_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        transport_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get route between two coordinates."""
        try:
            client = self._get_client()
            
            request = RouteRequest(
                start_lat=start_lat,
                start_lon=start_lon,
                end_lat=end_lat,
                end_lon=end_lon,
                mode=transport_mode or "foot",
                include_geometry=True
            )
            
            response = client.route(request)
            
            return {
                "summary": {
                    "total_distance_meters": response.summary.total_distance_meters,
                    "total_duration_seconds": response.summary.total_duration_seconds
                },
                "instructions": response.instructions,
                "geometry": getattr(response, "geometry", ""),
                "include_geometry": response.include_geometry
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    async def get_route_async(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        transport_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get route between two coordinates (async)."""
        try:
            client = self._get_client()
            
            request = RouteRequest(
                start_lat=start_lat,
                start_lon=start_lon,
                end_lat=end_lat,
                end_lon=end_lon,
                mode=transport_mode or "foot",
                include_geometry=True
            )
            
            response = await client.route_async(request)
            
            return {
                "summary": {
                    "total_distance_meters": response.summary.total_distance_meters,
                    "total_duration_seconds": response.summary.total_duration_seconds
                },
                "instructions": response.instructions,
                "geometry": getattr(response, "geometry", ""),
                "include_geometry": response.include_geometry
            }
        except APIError as e:
            raise ValueError(f"API Error: {e.message}")

    def close(self):
        """Close the client connection."""
        if self._client:
            # The SDK client doesn't have a close method in sync mode
            pass

    async def aclose(self):
        """Close the client connection (async)."""
        if self._client:
            await self._client.aclose()