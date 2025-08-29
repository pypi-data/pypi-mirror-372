#!/usr/bin/env python3
"""
Debug script to test the Camino AI SDK directly.
"""

import os
import traceback

def test_sdk_directly():
    """Test the SDK directly to isolate the issue."""
    print("🧪 Testing Camino AI SDK directly...")
    
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ No CAMINO_API_KEY found")
        return
    
    print(f"🔑 API Key: {api_key[:8]}...")
    
    try:
        from camino_ai import CaminoAI, APIError
        print("✅ SDK import successful")
        
        # Test with minimal configuration
        print("🔧 Creating client...")
        client = CaminoAI(api_key=api_key)
        print("✅ Client created successfully")
        
        # Try a simple query
        print("🔍 Testing simple query...")
        response = client.query(query="Eiffel Tower")
        print(f"✅ Query successful! Found {response.total} results")
        
        if response.results:
            first_result = response.results[0]
            print(f"   First result: {first_result.name}")
            print(f"   Coordinates: {first_result.lat}, {first_result.lon}")
        
    except APIError as e:
        print(f"❌ API Error: {e.message}")
        print(f"   Full error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("   Traceback:")
        traceback.print_exc()

def test_wrapper():
    """Test our SDK wrapper."""
    print("\n🔧 Testing SDK wrapper...")
    
    try:
        from langchain_camino._sdk_wrapper import CaminoSDKWrapper
        print("✅ Wrapper import successful")
        
        # Create wrapper
        wrapper = CaminoSDKWrapper()
        print("✅ Wrapper created successfully")
        
        # Test search
        print("🔍 Testing wrapper search...")
        result = wrapper.search_places("Eiffel Tower", limit=1)
        print(f"✅ Wrapper search successful! Found {result['total_results']} results")
        
        if result['places']:
            first_place = result['places'][0]
            print(f"   First place: {first_place['name']}")
            print(f"   Coordinates: {first_place['lat']}, {first_place['lon']}")
            
    except Exception as e:
        print(f"❌ Wrapper error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("   Traceback:")
        traceback.print_exc()

def test_langchain_tool():
    """Test the LangChain tool."""
    print("\n🛠️ Testing LangChain tool...")
    
    try:
        from langchain_camino import CaminoSearch
        print("✅ Tool import successful")
        
        # Create tool
        search = CaminoSearch()
        print("✅ Tool created successfully")
        
        # Test invoke
        print("🔍 Testing tool invoke...")
        result = search.invoke({"query": "Eiffel Tower", "limit": 1})
        print(f"✅ Tool invoke successful!")
        print(f"   Result: {result}")
        
    except Exception as e:
        print(f"❌ Tool error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("   Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    print("🐛 Debugging Camino AI SDK Integration")
    print("=" * 50)
    
    test_sdk_directly()
    test_wrapper()
    test_langchain_tool()
    
    print("\n✨ Debug tests completed!")