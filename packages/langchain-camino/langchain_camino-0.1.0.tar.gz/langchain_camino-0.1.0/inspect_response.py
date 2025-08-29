#!/usr/bin/env python3
"""
Script to inspect the actual response structure from Camino AI SDK.
"""

import os
from camino_ai import CaminoAI, QueryRequest

def inspect_response():
    """Inspect the actual response structure."""
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ No CAMINO_API_KEY found")
        return
    
    print("🔍 Inspecting Camino AI response structure...")
    
    try:
        client = CaminoAI(api_key=api_key)
        
        # Create request manually to avoid SDK bug
        request = QueryRequest(query="Eiffel Tower", limit=1)
        response = client.query(request)
        
        print(f"✅ Query successful! Found {response.total} results")
        print(f"📊 Response type: {type(response)}")
        print(f"📊 Response attributes: {dir(response)}")
        
        if response.results:
            first_result = response.results[0]
            print(f"\n🔍 First result type: {type(first_result)}")
            print(f"🔍 First result attributes: {dir(first_result)}")
            print(f"🔍 First result data: {first_result}")
            
            # Try to access common attributes
            attrs_to_check = ['name', 'lat', 'lon', 'latitude', 'longitude', 'location', 'address', 'category', 'description']
            for attr in attrs_to_check:
                try:
                    value = getattr(first_result, attr)
                    print(f"✅ {attr}: {value}")
                except AttributeError:
                    print(f"❌ {attr}: Not found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_response()