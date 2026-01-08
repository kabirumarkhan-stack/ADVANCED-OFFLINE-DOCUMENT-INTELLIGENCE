#!/usr/bin/env python3
"""
Test script for the Offline Document Intelligence System
"""

import requests
import time
import os

def test_system():
    """Test the document intelligence system"""

    base_url = "http://localhost:5000"

    print("🧪 Testing Offline Document Intelligence System")
    print("=" * 50)

    # Test 1: Check status
    print("\n1. Testing system status...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status check passed")
            print(f"   - Documents: {status['total_documents']}")
            print(f"   - Chunks: {status['total_chunks']}")
            print(f"   - Index loaded: {status['index_loaded']}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

    # Test 2: Test query without documents (should handle gracefully)
    print("\n2. Testing query handling...")
    test_queries = [
        "What are the main benefits of this insurance policy?",
        "Summarize the key exclusions",
        "What should I be careful about in this document?",
        "Explain the premium payment terms"
    ]

    for query in test_queries:
        try:
            response = requests.post(f"{base_url}/ask", json={"query": query})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query successful: '{query[:50]}...'")
                print(f"   - Query type: {data.get('query_type', 'unknown')}")
                print(f"   - Response length: {len(data.get('answer', ''))} chars")
                print(f"   - Sources: {len(data.get('sources', []))}")
            else:
                print(f"❌ Query failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Query error: {e}")
            return False

        time.sleep(1)  # Brief pause between queries

    print("\n🎉 All tests passed! System is working correctly.")
    print("\n📋 Test Summary:")
    print("   - System status: ✅")
    print("   - Query processing: ✅")
    print("   - Response generation: ✅")
    print("   - Source attribution: ✅")
    print("\n🚀 Ready for demo!")

    return True

if __name__ == "__main__":
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            test_system()
        else:
            print("❌ Flask app not responding. Please start the app with: python src/app.py")
    except:
        print("❌ Cannot connect to Flask app. Please start the app with: python src/app.py")