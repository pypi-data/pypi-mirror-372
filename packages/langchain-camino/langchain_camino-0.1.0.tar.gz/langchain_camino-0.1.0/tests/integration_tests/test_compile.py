"""Test that the integration can be imported and compiled."""

import pytest

def test_import_search():
    """Test that CaminoSearch can be imported."""
    from langchain_camino import CaminoSearch
    assert CaminoSearch is not None

def test_import_query():
    """Test that CaminoQuery can be imported."""
    from langchain_camino import CaminoQuery
    assert CaminoQuery is not None

def test_import_journey():
    """Test that CaminoJourney can be imported."""
    from langchain_camino import CaminoJourney
    assert CaminoJourney is not None

def test_import_all():
    """Test that all tools can be imported together."""
    from langchain_camino import CaminoSearch, CaminoQuery, CaminoJourney
    assert all([CaminoSearch, CaminoQuery, CaminoJourney])

@pytest.mark.compile
def test_tools_instantiate():
    """Test that tools can be instantiated without API key for compilation."""
    import os
    from unittest.mock import patch
    
    # Mock environment variable for compilation test
    with patch.dict(os.environ, {"CAMINO_API_KEY": "test-key"}):
        from langchain_camino import CaminoSearch, CaminoQuery, CaminoJourney
        
        search = CaminoSearch()
        query = CaminoQuery()
        journey = CaminoJourney()
        
        assert search.name == "camino_search"
        assert query.name == "camino_query" 
        assert journey.name == "camino_journey"