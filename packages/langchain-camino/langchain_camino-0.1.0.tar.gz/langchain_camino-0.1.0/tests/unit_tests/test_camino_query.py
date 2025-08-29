"""Unit tests for CaminoQuery."""

import pytest
from unittest.mock import Mock, patch
from langchain_core.tools import ToolException

from langchain_camino import CaminoQuery


class TestCaminoQuery:
    """Test CaminoQuery tool."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict("os.environ", {"CAMINO_API_KEY": "test-key"}):
            self.tool = CaminoQuery()

    def test_init(self):
        """Test CaminoQuery initialization."""
        assert self.tool.name == "camino_query"
        assert "natural language location queries" in self.tool.description
        assert self.tool.api_wrapper is not None

    def test_init_with_custom_params(self):
        """Test CaminoQuery initialization with custom parameters."""
        with patch.dict("os.environ", {"CAMINO_API_KEY": "test-key"}):
            tool = CaminoQuery(limit=20, ai_ranking=False)
            assert tool.limit == 20
            assert tool.ai_ranking == False

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.query_locations")
    def test_run_success(self, mock_query):
        """Test successful query execution."""
        # Mock API response
        mock_response = {
            "results": [
                {
                    "name": "Test Restaurant",
                    "lat": 37.7749,
                    "lon": -122.4194,
                    "distance": 0.5,
                    "type": "restaurant",
                    "rating": 4.5
                }
            ],
            "query": "restaurants near me",
            "total_results": 1,
            "ai_ranked": True
        }
        mock_query.return_value = mock_response

        result = self.tool._run(
            query="restaurants near me",
            lat=37.7749,
            lon=-122.4194,
            radius=1.0,
            limit=10,
            ai_ranking=True
        )
        
        assert result == mock_response
        mock_query.assert_called_once_with(
            query="restaurants near me",
            lat=37.7749,
            lon=-122.4194,
            radius=1.0,
            limit=10,
            rank=True
        )

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.query_locations")
    def test_run_no_results(self, mock_query):
        """Test query with no results."""
        mock_query.return_value = {"results": [], "query": "test", "total_results": 0}

        with pytest.raises(ToolException) as exc_info:
            self.tool._run("test query")
        
        assert "No results found" in str(exc_info.value)

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.query_locations")
    def test_run_api_error(self, mock_query):
        """Test query with API error."""
        mock_query.side_effect = ValueError("API Error")

        result = self.tool._run("test query")
        
        assert "error" in result
        assert result["error"] == "API Error"

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.query_locations_async")
    async def test_arun_success(self, mock_query_async):
        """Test successful async query execution."""
        mock_response = {
            "results": [{"name": "Test Place", "lat": 37.7749, "lon": -122.4194}],
            "query": "test query",
            "total_results": 1
        }
        mock_query_async.return_value = mock_response

        result = await self.tool._arun("test query", limit=5)
        
        assert result == mock_response
        mock_query_async.assert_called_once_with(
            query="test query",
            lat=None,
            lon=None,
            radius=None,
            limit=5,
            rank=None,
            offset=None,
            answer=None
        )

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.query_locations_async")
    async def test_arun_no_results(self, mock_query_async):
        """Test async query with no results."""
        mock_query_async.return_value = {"results": [], "query": "test", "total_results": 0}

        with pytest.raises(ToolException) as exc_info:
            await self.tool._arun("test query")
        
        assert "No results found" in str(exc_info.value)

    def test_invoke_integration(self):
        """Test invoke method integration."""
        with patch.object(self.tool, "_run") as mock_run:
            mock_run.return_value = {"results": [], "total_results": 0}
            
            result = self.tool.invoke({
                "query": "test",
                "lat": 37.7749,
                "lon": -122.4194
            })
            
            # The invoke method passes arguments by keyword
            mock_run.assert_called_once_with(
                query="test",
                lat=37.7749,
                lon=-122.4194
            )