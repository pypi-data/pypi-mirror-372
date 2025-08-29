"""Unit tests for CaminoJourney."""

import pytest
from unittest.mock import Mock, patch
from langchain_core.tools import ToolException

from langchain_camino import CaminoJourney


class TestCaminoJourney:
    """Test CaminoJourney tool."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict("os.environ", {"CAMINO_API_KEY": "test-key"}):
            self.tool = CaminoJourney()

    def test_init(self):
        """Test CaminoJourney initialization."""
        assert self.tool.name == "camino_journey"
        assert "multi-waypoint journeys" in self.tool.description
        assert self.tool.api_wrapper is not None

    def test_init_with_custom_params(self):
        """Test CaminoJourney initialization with custom parameters."""
        with patch.dict("os.environ", {"CAMINO_API_KEY": "test-key"}):
            tool = CaminoJourney(transport_mode="bike", optimize=False)
            assert tool.transport_mode == "bike"
            assert tool.optimize == False

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.plan_journey")
    def test_run_success(self, mock_journey):
        """Test successful journey planning execution."""
        # Mock API response
        mock_response = {
            "journey": {
                "total_distance": 15.2,
                "total_duration": 1800,
                "optimized": True,
                "transport_mode": "car",
                "waypoints": [
                    {"lat": 37.7749, "lon": -122.4194, "order": 0},
                    {"lat": 37.7849, "lon": -122.4094, "order": 1}
                ],
                "route_geometry": "encoded_geometry",
                "instructions": ["Turn left", "Go straight"]
            }
        }
        mock_journey.return_value = mock_response

        waypoints = [(37.7749, -122.4194), (37.7849, -122.4094)]
        result = self.tool._run(
            waypoints=waypoints,
            transport_mode="car",
            optimize=True
        )
        
        assert result == mock_response
        mock_journey.assert_called_once_with(
            waypoints=waypoints,
            transport_mode="car",
            optimize=True
        )

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.plan_journey")
    def test_run_insufficient_waypoints(self, mock_journey):
        """Test journey planning with insufficient waypoints."""
        waypoints = [(37.7749, -122.4194)]  # Only one waypoint

        with pytest.raises(ToolException) as exc_info:
            self.tool._run(waypoints=waypoints)
        
        assert "At least 2 waypoints are required" in str(exc_info.value)

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.plan_journey")
    def test_run_no_journey(self, mock_journey):
        """Test journey planning with no route found."""
        mock_journey.return_value = {"journey": None}
        waypoints = [(37.7749, -122.4194), (37.7849, -122.4094)]

        with pytest.raises(ToolException) as exc_info:
            self.tool._run(waypoints=waypoints)
        
        assert "Could not plan journey" in str(exc_info.value)

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.plan_journey")
    def test_run_api_error(self, mock_journey):
        """Test journey planning with API error."""
        mock_journey.side_effect = ValueError("API Error")
        waypoints = [(37.7749, -122.4194), (37.7849, -122.4094)]

        result = self.tool._run(waypoints=waypoints)
        
        assert "error" in result
        assert result["error"] == "API Error"

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.plan_journey_async")
    async def test_arun_success(self, mock_journey_async):
        """Test successful async journey planning execution."""
        mock_response = {
            "journey": {
                "total_distance": 10.0,
                "total_duration": 1200,
                "waypoints": [
                    {"lat": 37.7749, "lon": -122.4194, "order": 0},
                    {"lat": 37.7849, "lon": -122.4094, "order": 1}
                ]
            }
        }
        mock_journey_async.return_value = mock_response

        waypoints = [(37.7749, -122.4194), (37.7849, -122.4094)]
        result = await self.tool._arun(waypoints=waypoints)
        
        assert result == mock_response
        mock_journey_async.assert_called_once_with(
            waypoints=waypoints,
            transport_mode=None,
            optimize=None
        )

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.plan_journey_async")
    async def test_arun_insufficient_waypoints(self, mock_journey_async):
        """Test async journey planning with insufficient waypoints."""
        waypoints = [(37.7749, -122.4194)]

        with pytest.raises(ToolException) as exc_info:
            await self.tool._arun(waypoints=waypoints)
        
        assert "At least 2 waypoints are required" in str(exc_info.value)

    def test_invoke_integration(self):
        """Test invoke method integration."""
        with patch.object(self.tool, "_run") as mock_run:
            mock_run.return_value = {"journey": {}}
            waypoints = [(37.7749, -122.4194), (37.7849, -122.4094)]
            
            result = self.tool.invoke({
                "waypoints": waypoints,
                "transport_mode": "car"
            })
            
            # The invoke method passes arguments by keyword
            mock_run.assert_called_once_with(
                waypoints=waypoints,
                transport_mode="car"
            )