"""Camino search tools."""

from typing import Any, Dict, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field

from langchain_camino._sdk_wrapper import CaminoSDKWrapper


class CaminoSearchInput(BaseModel):
    """Input for [CaminoSearch]"""

    query: str = Field(description="Name of the place to search for")
    limit: Optional[int] = Field(
        default=5,
        description="Maximum number of search results to return. Default is 5."
    )


class CaminoSearch(BaseTool):
    """Tool that queries the Camino Search API for places by name.

    Setup:
        Install ``langchain-camino`` and set environment variable ``CAMINO_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-camino
            export CAMINO_API_KEY="your-api-key"

    Instantiate:

        .. code-block:: python
            from langchain_camino import CaminoSearch

            tool = CaminoSearch(
                limit=10,
                # camino_api_key="your-api-key", # if not using env variable
            )

    Invoke directly with args:

        .. code-block:: python

            tool.invoke({"query": "coffee shops in San Francisco"})

        .. code-block:: json

            {
                'places': [
                    {
                        'name': 'Blue Bottle Coffee',
                        'lat': 37.7749,
                        'lon': -122.4194,
                        'address': '66 Mint St, San Francisco, CA',
                        'place_type': 'cafe'
                    }
                ],
                'query': 'coffee shops in San Francisco',
                'total_results': 1
            }

    """

    name: str = "camino_search"
    description: str = (
        "Search for places by name using the Camino AI Reality Grounding API. "
        "This tool uses Nominatim for location lookup and returns detailed place "
        "information including coordinates, addresses, and place types. "
        "Useful for finding specific locations, businesses, landmarks, or points of interest."
    )

    args_schema: Type[BaseModel] = CaminoSearchInput
    handle_tool_error: bool = True

    limit: Optional[int] = None
    """Maximum number of search results to return. Default is 5."""

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
        limit: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Execute a place search using the Camino Search API.

        Returns:
            Dict[str, Any]: Search results containing:
                - places: List of place results, each with:
                    - name: Name of the place
                    - lat: Latitude coordinate
                    - lon: Longitude coordinate 
                    - address: Full address
                    - place_type: Type of place (e.g., cafe, restaurant)
                - query: Original search query
                - total_results: Number of results found
        """
        try:
            # Execute search with parameters
            raw_results = self.api_wrapper.search_places(
                query=query,
                limit=self.limit if self.limit else limit,
            )

            # Check if results are empty and raise a specific exception
            if not raw_results.get("places", []):
                error_message = (
                    f"No places found for '{query}'. "
                    f"Try using a different place name or be more specific with the location."
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
        limit: Optional[int] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Use the tool asynchronously."""
        try:
            raw_results = await self.api_wrapper.search_places_async(
                query=query,
                limit=self.limit if self.limit else limit,
            )

            # Check if results are empty and raise a specific exception
            if not raw_results.get("places", []):
                error_message = (
                    f"No places found for '{query}'. "
                    f"Try using a different place name or be more specific with the location."
                )
                raise ToolException(error_message)

            return raw_results
        except ToolException:
            # Re-raise tool exceptions
            raise
        except Exception as e:
            return {"error": str(e)}