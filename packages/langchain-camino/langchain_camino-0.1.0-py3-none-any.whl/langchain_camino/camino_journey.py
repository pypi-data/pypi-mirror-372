"""Camino journey tools."""

from typing import Any, Dict, List, Optional, Tuple, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field

from langchain_camino._sdk_wrapper import CaminoSDKWrapper


class CaminoJourneyInput(BaseModel):
    """Input for [CaminoJourney]"""

    waypoints: List[Tuple[float, float]] = Field(
        description="List of waypoints as (latitude, longitude) tuples for the journey"
    )
    transport_mode: Optional[str] = Field(
        default="car",
        description="Mode of transport: 'car', 'bike', 'foot', or 'transit'. Default is 'car'."
    )
    optimize: Optional[bool] = Field(
        default=True,
        description="Whether to optimize the route for shortest time/distance. Default is True."
    )


class CaminoJourney(BaseTool):
    """Tool that plans multi-waypoint journeys using the Camino API.

    Setup:
        Install ``langchain-camino`` and set environment variable ``CAMINO_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-camino
            export CAMINO_API_KEY="your-api-key"

    Instantiate:

        .. code-block:: python
            from langchain_camino import CaminoJourney

            tool = CaminoJourney(
                transport_mode="car",
                optimize=True,
                # camino_api_key="your-api-key", # if not using env variable
            )

    Invoke directly with args:

        .. code-block:: python

            tool.invoke({
                "waypoints": [(37.7749, -122.4194), (37.7849, -122.4094), (37.7949, -122.3994)],
                "transport_mode": "car",
                "optimize": True
            })

        .. code-block:: json

            {
                'journey': {
                    'total_distance': 15.2,
                    'total_duration': 1800,
                    'optimized': True,
                    'transport_mode': 'car',
                    'waypoints': [
                        {'lat': 37.7749, 'lon': -122.4194, 'order': 0},
                        {'lat': 37.7849, 'lon': -122.4094, 'order': 1},
                        {'lat': 37.7949, 'lon': -122.3994, 'order': 2}
                    ],
                    'route_geometry': '...',
                    'instructions': [...]
                }
            }

    """

    name: str = "camino_journey"
    description: str = (
        "Plan multi-waypoint journeys using the Camino AI Reality Grounding API. "
        "This tool provides route optimization, supports different transport modes, "
        "and handles complex journey planning with multiple stops. "
        "Useful for planning trips with multiple destinations, delivery routes, "
        "or sightseeing tours with optimized routing."
    )

    args_schema: Type[BaseModel] = CaminoJourneyInput
    handle_tool_error: bool = True

    transport_mode: Optional[str] = None
    """Default transport mode: 'car', 'bike', 'foot', or 'transit'. Default is 'car'."""
    
    optimize: Optional[bool] = None
    """Whether to optimize routes by default. Default is True."""

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
        waypoints: List[Tuple[float, float]],
        transport_mode: Optional[str] = None,
        optimize: Optional[bool] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Plan a multi-waypoint journey using the Camino Journey API.

        Returns:
            Dict[str, Any]: Journey results containing:
                - journey: Journey details with:
                    - total_distance: Total distance in kilometers
                    - total_duration: Total duration in seconds
                    - optimized: Whether the route was optimized
                    - transport_mode: Mode of transport used
                    - waypoints: List of waypoints with order
                    - route_geometry: Encoded route geometry
                    - instructions: Turn-by-turn directions
        """
        try:
            # Validate waypoints
            if len(waypoints) < 2:
                raise ToolException("At least 2 waypoints are required for journey planning")

            # Execute journey planning with parameters
            raw_results = self.api_wrapper.plan_journey(
                waypoints=waypoints,
                transport_mode=self.transport_mode if self.transport_mode else transport_mode,
                optimize=self.optimize if self.optimize is not None else optimize,
            )

            # Check if journey planning failed
            if not raw_results.get("journey"):
                error_message = (
                    f"Could not plan journey with {len(waypoints)} waypoints. "
                    f"Please check that all coordinates are valid and accessible."
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
        waypoints: List[Tuple[float, float]],
        transport_mode: Optional[str] = None,
        optimize: Optional[bool] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Use the tool asynchronously."""
        try:
            # Validate waypoints
            if len(waypoints) < 2:
                raise ToolException("At least 2 waypoints are required for journey planning")

            raw_results = await self.api_wrapper.plan_journey_async(
                waypoints=waypoints,
                transport_mode=self.transport_mode if self.transport_mode else transport_mode,
                optimize=self.optimize if self.optimize is not None else optimize,
            )

            # Check if journey planning failed
            if not raw_results.get("journey"):
                error_message = (
                    f"Could not plan journey with {len(waypoints)} waypoints. "
                    f"Please check that all coordinates are valid and accessible."
                )
                raise ToolException(error_message)

            return raw_results
        except ToolException:
            # Re-raise tool exceptions
            raise
        except Exception as e:
            return {"error": str(e)}