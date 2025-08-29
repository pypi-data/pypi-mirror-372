"""Camino query tools."""

from typing import Any, Dict, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field

from langchain_camino._sdk_wrapper import CaminoSDKWrapper


class CaminoQueryInput(BaseModel):
    """Input for [CaminoQuery]"""

    query: str = Field(description="Natural language query for location-based search")
    lat: Optional[float] = Field(
        default=None,
        description="Latitude coordinate for location-based search context"
    )
    lon: Optional[float] = Field(
        default=None,
        description="Longitude coordinate for location-based search context"
    )
    radius: Optional[float] = Field(
        default=None,
        description="Search radius in kilometers from the provided coordinates"
    )
    limit: Optional[int] = Field(
        default=10,
        description="Maximum number of results to return. Default is 10."
    )
    ai_ranking: Optional[bool] = Field(
        default=True,
        description="Whether to use AI-powered result ranking for better relevance. Default is True."
    )


class CaminoQuery(BaseTool):
    """Tool that makes natural language location queries using the Camino API.

    Setup:
        Install ``langchain-camino`` and set environment variable ``CAMINO_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-camino
            export CAMINO_API_KEY="your-api-key"

    Instantiate:

        .. code-block:: python
            from langchain_camino import CaminoQuery

            tool = CaminoQuery(
                limit=20,
                ai_ranking=True,
                # camino_api_key="your-api-key", # if not using env variable
            )

    Invoke directly with args:

        .. code-block:: python

            tool.invoke({
                "query": "Find good restaurants near me", 
                "lat": 37.7749,
                "lon": -122.4194,
                "radius": 1.0
            })

        .. code-block:: json

            {
                'results': [
                    {
                        'name': 'The French Laundry',
                        'lat': 37.7751,
                        'lon': -122.4180,
                        'distance': 0.2,
                        'type': 'restaurant',
                        'rating': 4.8
                    }
                ],
                'query': 'Find good restaurants near me',
                'total_results': 1,
                'ai_ranked': True
            }

    """

    name: str = "camino_query"
    description: str = (
        "Make natural language location queries using the Camino AI Reality Grounding API. "
        "This tool converts natural language queries to location searches and supports "
        "location-based POI discovery with optional AI-powered result ranking. "
        "Useful for finding places based on descriptive queries like 'coffee shops near me', "
        "'best restaurants in downtown', or 'parks within walking distance'."
    )

    args_schema: Type[BaseModel] = CaminoQueryInput
    handle_tool_error: bool = True

    limit: Optional[int] = None
    """Maximum number of results to return. Default is 10."""
    
    ai_ranking: Optional[bool] = None
    """Whether to use AI-powered result ranking. Default is True."""

    api_wrapper: CaminoSDKWrapper = Field(default_factory=CaminoSDKWrapper)

    def __init__(self, **kwargs: Any) -> None:
        # Create api_wrapper with camino_api_key if provided
        if "camino_api_key" in kwargs or "api_base_url" in kwargs:
            wrapper_kwargs = {}
            if "camino_api_key" in kwargs:
                wrapper_kwargs["camino_api_key"] = kwargs["camino_api_key"]
            if "api_base_url" in kwargs:
                wrapper_kwargs["api_base_url"] = kwargs["api_base_url"]
            kwargs["api_wrapper"] = CaminoSDKWrapper(**wrapper_kwargs)

        super().__init__(**kwargs)

    def _run(
        self,
        query: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[float] = None,
        limit: Optional[int] = None,
        ai_ranking: Optional[bool] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Execute a natural language location query using the Camino Query API.

        Returns:
            Dict[str, Any]: Query results containing:
                - results: List of location results, each with:
                    - name: Name of the location
                    - lat: Latitude coordinate
                    - lon: Longitude coordinate
                    - distance: Distance from search center (if provided)
                    - type: Type of location/POI
                    - additional metadata
                - query: Original search query
                - total_results: Number of results found
                - ai_ranked: Whether AI ranking was applied
        """
        try:
            # Execute query with parameters
            raw_results = self.api_wrapper.query_locations(
                query=query,
                lat=lat,
                lon=lon,
                radius=radius,
                limit=self.limit if self.limit else limit,
                rank=self.ai_ranking if self.ai_ranking is not None else ai_ranking,
            )

            # Check if results are empty and raise a specific exception
            if not raw_results.get("results", []):
                error_message = (
                    f"No results found for '{query}'. "
                    f"Try rephrasing your query or expanding your search area."
                )
                raise ToolException(error_message)

            return raw_results
        except ToolException:
            # Re-raise tool exceptions
            raise
        except Exception as e:
            return {"error": str(e)}

    async def _arun(
        self,
        query: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[float] = None,
        limit: Optional[int] = None,
        ai_ranking: Optional[bool] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Use the tool asynchronously."""
        try:
            raw_results = await self.api_wrapper.query_locations_async(
                query=query,
                lat=lat,
                lon=lon,
                radius=radius,
                limit=self.limit if self.limit else limit,
                rank=self.ai_ranking if self.ai_ranking is not None else ai_ranking,
            )

            # Check if results are empty and raise a specific exception
            if not raw_results.get("results", []):
                error_message = (
                    f"No results found for '{query}'. "
                    f"Try rephrasing your query or expanding your search area."
                )
                raise ToolException(error_message)

            return raw_results
        except ToolException:
            # Re-raise tool exceptions
            raise
        except Exception as e:
            return {"error": str(e)}