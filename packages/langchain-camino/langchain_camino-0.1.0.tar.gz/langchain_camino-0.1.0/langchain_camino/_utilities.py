"""Util that calls Camino API.

In order to set this up, follow instructions at:
https://docs.getcamino.ai/
"""

import json
from typing import Any, Dict, List, Optional, Tuple, Union

import aiohttp
import requests
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, SecretStr, model_validator


CAMINO_API_URL: str = "https://app.getcamino.ai"


class CaminoAPIWrapper(BaseModel):
    """Wrapper for Camino API."""

    camino_api_key: SecretStr
    api_base_url: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        """Validate that api key and endpoint exists in environment."""
        camino_api_key = get_from_dict_or_env(
            values, "camino_api_key", "CAMINO_API_KEY"
        )
        values["camino_api_key"] = camino_api_key

        return values

    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests."""
        return {
            "X-API-Key": self.camino_api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

    def search_places(
        self,
        q: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search for places by name using Nominatim."""
        params = {
            "q": q,
        }
        
        if limit is not None:
            params["limit"] = limit

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        response = requests.post(
            f"{base_url}/search",
            json=params,
            headers=self._get_headers(),
        )
        
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def search_places_async(
        self,
        q: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search for places by name using Nominatim asynchronously."""
        params = {
            "q": q,
        }
        
        if limit is not None:
            params["limit"] = limit

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/search", json=params, headers=self._get_headers()
            ) as res:
                if res.status == 200:
                    data = await res.text()
                    return json.loads(data)
                else:
                    raise ValueError(f"Error {res.status}: {await res.text()}")

    def query_locations(
        self,
        q: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[float] = None,
        limit: Optional[int] = None,
        rank: Optional[bool] = None,
        offset: Optional[int] = None,
        answer: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Make natural language location queries."""
        params = {
            "q": q,
        }
        
        if lat is not None:
            params["lat"] = lat
        if lon is not None:
            params["lon"] = lon
        if radius is not None:
            params["radius"] = radius
        if limit is not None:
            params["limit"] = limit
        if rank is not None:
            params["rank"] = rank
        if offset is not None:
            params["offset"] = offset
        if answer is not None:
            params["answer"] = answer

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        response = requests.get(
            f"{base_url}/query",
            params=params,
            headers=self._get_headers(),
        )
        
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def query_locations_async(
        self,
        q: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[float] = None,
        limit: Optional[int] = None,
        rank: Optional[bool] = None,
        offset: Optional[int] = None,
        answer: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Make natural language location queries asynchronously."""
        params = {
            "q": q,
        }
        
        if lat is not None:
            params["lat"] = lat
        if lon is not None:
            params["lon"] = lon
        if radius is not None:
            params["radius"] = radius
        if limit is not None:
            params["limit"] = limit
        if rank is not None:
            params["rank"] = rank
        if offset is not None:
            params["offset"] = offset
        if answer is not None:
            params["answer"] = answer

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/query", 
                params=params,
                headers=self._get_headers()
            ) as res:
                if res.status == 200:
                    data = await res.text()
                    return json.loads(data)
                else:
                    raise ValueError(f"Error {res.status}: {await res.text()}")

    def plan_journey(
        self,
        waypoints: List[Tuple[float, float]],
        transport_mode: Optional[str] = None,
        optimize: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Plan multi-waypoint journeys."""
        params = {
            "waypoints": waypoints,
        }
        
        if transport_mode is not None:
            params["transport_mode"] = transport_mode
        if optimize is not None:
            params["optimize"] = optimize

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        response = requests.post(
            f"{base_url}/journey",
            json=params,
            headers=self._get_headers(),
        )
        
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def plan_journey_async(
        self,
        waypoints: List[Tuple[float, float]],
        transport_mode: Optional[str] = None,
        optimize: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Plan multi-waypoint journeys asynchronously."""
        params = {
            "waypoints": waypoints,
        }
        
        if transport_mode is not None:
            params["transport_mode"] = transport_mode
        if optimize is not None:
            params["optimize"] = optimize

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/journey", json=params, headers=self._get_headers()
            ) as res:
                if res.status == 200:
                    data = await res.text()
                    return json.loads(data)
                else:
                    raise ValueError(f"Error {res.status}: {await res.text()}")

    def get_spatial_relationship(
        self,
        location1: Tuple[float, float],
        location2: Tuple[float, float],
        include_travel_time: Optional[bool] = None,
        transport_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate spatial relationships between locations."""
        params = {
            "location1": location1,
            "location2": location2,
        }
        
        if include_travel_time is not None:
            params["include_travel_time"] = include_travel_time
        if transport_mode is not None:
            params["transport_mode"] = transport_mode

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        response = requests.post(
            f"{base_url}/relationship",
            json=params,
            headers=self._get_headers(),
        )
        
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def get_spatial_relationship_async(
        self,
        location1: Tuple[float, float],
        location2: Tuple[float, float],
        include_travel_time: Optional[bool] = None,
        transport_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate spatial relationships between locations asynchronously."""
        params = {
            "location1": location1,
            "location2": location2,
        }
        
        if include_travel_time is not None:
            params["include_travel_time"] = include_travel_time
        if transport_mode is not None:
            params["transport_mode"] = transport_mode

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/relationship", json=params, headers=self._get_headers()
            ) as res:
                if res.status == 200:
                    data = await res.text()
                    return json.loads(data)
                else:
                    raise ValueError(f"Error {res.status}: {await res.text()}")

    def get_location_context(
        self,
        lat: float,
        lon: float,
        radius: Optional[float] = None,
        include_accessibility: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get contextual information about a location."""
        params = {
            "lat": lat,
            "lon": lon,
        }
        
        if radius is not None:
            params["radius"] = radius
        if include_accessibility is not None:
            params["include_accessibility"] = include_accessibility

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        response = requests.post(
            f"{base_url}/context",
            json=params,
            headers=self._get_headers(),
        )
        
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def get_location_context_async(
        self,
        lat: float,
        lon: float,
        radius: Optional[float] = None,
        include_accessibility: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get contextual information about a location asynchronously."""
        params = {
            "lat": lat,
            "lon": lon,
        }
        
        if radius is not None:
            params["radius"] = radius
        if include_accessibility is not None:
            params["include_accessibility"] = include_accessibility

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/context", json=params, headers=self._get_headers()
            ) as res:
                if res.status == 200:
                    data = await res.text()
                    return json.loads(data)
                else:
                    raise ValueError(f"Error {res.status}: {await res.text()}")

    def get_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        transport_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get route between two coordinates."""
        params = {
            "start_lat": start_lat,
            "start_lon": start_lon,
            "end_lat": end_lat,
            "end_lon": end_lon,
        }
        
        if transport_mode is not None:
            params["transport_mode"] = transport_mode

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        response = requests.get(
            f"{base_url}/route",
            params=params,
            headers=self._get_headers(),
        )
        
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def get_route_async(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        transport_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get route between two coordinates asynchronously."""
        params = {
            "start_lat": start_lat,
            "start_lon": start_lon,
            "end_lat": end_lat,
            "end_lon": end_lon,
        }
        
        if transport_mode is not None:
            params["transport_mode"] = transport_mode

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        base_url = self.api_base_url or CAMINO_API_URL
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/route", 
                params=params,
                headers=self._get_headers()
            ) as res:
                if res.status == 200:
                    data = await res.text()
                    return json.loads(data)
                else:
                    raise ValueError(f"Error {res.status}: {await res.text()}")