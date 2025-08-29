"""Unit tests for CaminoSearch."""

import pytest
from unittest.mock import Mock, patch
from langchain_core.tools import ToolException

from langchain_camino import CaminoSearch


class TestCaminoSearch:
    """Test CaminoSearch tool."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict("os.environ", {"CAMINO_API_KEY": "test-key"}):
            self.tool = CaminoSearch()

    def test_init(self):
        """Test CaminoSearch initialization."""
        assert self.tool.name == "camino_search"
        assert "Camino AI Reality Grounding API" in self.tool.description
        assert self.tool.api_wrapper is not None

    def test_init_with_custom_params(self):
        """Test CaminoSearch initialization with custom parameters."""
        with patch.dict("os.environ", {"CAMINO_API_KEY": "test-key"}):
            tool = CaminoSearch(limit=20)
            assert tool.limit == 20

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.search_places")
    def test_run_success(self, mock_search):
        """Test successful search execution."""
        # Mock API response
        mock_response = {
            "places": [
                {
                    "name": "Test Place",
                    "lat": 37.7749,
                    "lon": -122.4194,
                    "address": "123 Test St, San Francisco, CA",
                    "place_type": "restaurant"
                }
            ],
            "query": "test query",
            "total_results": 1
        }
        mock_search.return_value = mock_response

        result = self.tool._run("test query", limit=5)
        
        assert result == mock_response
        mock_search.assert_called_once_with(
            query="test query",
            limit=5
        )

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.search_places")
    def test_run_no_results(self, mock_search):
        """Test search with no results."""
        mock_search.return_value = {"places": [], "query": "test", "total_results": 0}

        with pytest.raises(ToolException) as exc_info:
            self.tool._run("test query")
        
        assert "No places found" in str(exc_info.value)

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.search_places")
    def test_run_api_error(self, mock_search):
        """Test search with API error."""
        mock_search.side_effect = ValueError("API Error")

        result = self.tool._run("test query")
        
        assert "error" in result
        assert result["error"] == "API Error"

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.search_places_async")
    async def test_arun_success(self, mock_search_async):
        """Test successful async search execution."""
        mock_response = {
            "places": [{"name": "Test Place", "lat": 37.7749, "lon": -122.4194}],
            "query": "test query",
            "total_results": 1
        }
        mock_search_async.return_value = mock_response

        result = await self.tool._arun("test query", limit=5)
        
        assert result == mock_response
        mock_search_async.assert_called_once_with(
            query="test query",
            limit=5
        )

    @patch("langchain_camino._sdk_wrapper.CaminoSDKWrapper.search_places_async")
    async def test_arun_no_results(self, mock_search_async):
        """Test async search with no results."""
        mock_search_async.return_value = {"places": [], "query": "test", "total_results": 0}

        with pytest.raises(ToolException) as exc_info:
            await self.tool._arun("test query")
        
        assert "No places found" in str(exc_info.value)

    def test_invoke_integration(self):
        """Test invoke method integration."""
        with patch.object(self.tool, "_run") as mock_run:
            mock_run.return_value = {"places": [], "total_results": 0}
            
            result = self.tool.invoke({"query": "test"})
            
            # The invoke method passes arguments by keyword
            mock_run.assert_called_once_with(query="test")