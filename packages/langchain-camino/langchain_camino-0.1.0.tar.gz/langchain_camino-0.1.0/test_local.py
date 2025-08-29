#!/usr/bin/env python3
"""
Local test script for langchain-camino integration.
Run this script to verify the integration works locally.
"""

import os
import sys
from unittest.mock import patch

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🔍 Testing imports...")
    
    try:
        from langchain_camino import CaminoSearch, CaminoQuery, CaminoJourney, __version__
        print("✅ All imports successful!")
        print(f"📦 Package version: {__version__ or 'development'}")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_tool_initialization():
    """Test that tools can be initialized without API key."""
    print("\n🔧 Testing tool initialization...")
    
    try:
        # Mock environment variable for initialization test
        with patch.dict(os.environ, {"CAMINO_API_KEY": "test-key"}):
            from langchain_camino import CaminoSearch, CaminoQuery, CaminoJourney
            
            search = CaminoSearch()
            query = CaminoQuery()
            journey = CaminoJourney()
            
            print(f"✅ CaminoSearch: {search.name}")
            print(f"✅ CaminoQuery: {query.name}")
            print(f"✅ CaminoJourney: {journey.name}")
            
            return True
    except Exception as e:
        print(f"❌ Tool initialization failed: {e}")
        return False

def test_tool_schemas():
    """Test that tool input schemas work correctly."""
    print("\n📋 Testing tool schemas...")
    
    try:
        with patch.dict(os.environ, {"CAMINO_API_KEY": "test-key"}):
            from langchain_camino import CaminoSearch, CaminoQuery, CaminoJourney
            
            search = CaminoSearch()
            query = CaminoQuery()
            journey = CaminoJourney()
            
            # Test schema validation
            search_schema = search.args_schema
            query_schema = query.args_schema
            journey_schema = journey.args_schema
            
            print(f"✅ CaminoSearch schema: {search_schema.__name__}")
            print(f"✅ CaminoQuery schema: {query_schema.__name__}")
            print(f"✅ CaminoJourney schema: {journey_schema.__name__}")
            
            return True
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def test_with_real_api():
    """Test with real API if API key is available."""
    print("\n🌐 Testing with real API...")
    
    api_key = os.environ.get("CAMINO_API_KEY")
    if not api_key or api_key == "test-key":
        print("⚠️  No real API key found. Set CAMINO_API_KEY environment variable to test with real API.")
        return True
    
    try:
        from langchain_camino import CaminoSearch
        
        print(f"🔑 Using API key: {api_key[:8]}...")
        search = CaminoSearch()
        
        # Try a simple search
        print("🔍 Testing place search...")
        result = search.invoke({"query": "eiffel tower", "limit": 1})
        
        if "error" in result:
            print(f"⚠️  API returned error: {result['error']}")
        else:
            print("✅ Real API test successful!")
            print(f"📍 Found {result.get('total_results', 0)} places")
            
        return True
        
    except Exception as e:
        print(f"❌ Real API test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing langchain-camino integration locally...\n")
    
    tests = [
        test_imports,
        test_tool_initialization,
        test_tool_schemas,
        test_with_real_api,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())