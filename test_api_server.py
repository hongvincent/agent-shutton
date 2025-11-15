#!/usr/bin/env python3
"""Test API server endpoints."""

import asyncio
import httpx
import subprocess
import time
import sys

print("=" * 80)
print("Testing MedResearch AI API Server")
print("=" * 80)

# Start server in background
print("\n[1] Starting API server...")
server_process = subprocess.Popen(
    ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
print("   Waiting for server to start...")
time.sleep(3)

try:
    async def test_endpoints():
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=10.0) as client:
            # Test 1: Root endpoint
            print("\n[Test 1] Testing root endpoint (/)...")
            try:
                response = await client.get("/")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                print(f"✅ Root endpoint: {data['status']} (version {data['version']})")
            except Exception as e:
                print(f"❌ Root endpoint: FAILED - {e}")

            # Test 2: Health endpoint
            print("\n[Test 2] Testing health endpoint (/health)...")
            try:
                response = await client.get("/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                print(f"✅ Health endpoint: {data['status']}")
            except Exception as e:
                print(f"❌ Health endpoint: FAILED - {e}")

            # Test 3: List sessions endpoint
            print("\n[Test 3] Testing list sessions endpoint (/sessions)...")
            try:
                response = await client.get("/sessions")
                assert response.status_code == 200
                data = response.json()
                assert "total" in data
                assert "sessions" in data
                print(f"✅ List sessions: {data['total']} sessions found")
            except Exception as e:
                print(f"❌ List sessions: FAILED - {e}")

            # Test 4: Metrics endpoint
            print("\n[Test 4] Testing metrics endpoint (/metrics)...")
            try:
                response = await client.get("/metrics")
                assert response.status_code == 200
                data = response.json()
                assert "timestamp" in data
                print(f"✅ Metrics endpoint: OK")
            except Exception as e:
                print(f"❌ Metrics endpoint: FAILED - {e}")

            # Test 5: OpenAPI docs
            print("\n[Test 5] Testing OpenAPI docs (/docs)...")
            try:
                response = await client.get("/docs")
                assert response.status_code == 200
                print(f"✅ OpenAPI docs: accessible")
            except Exception as e:
                print(f"❌ OpenAPI docs: FAILED - {e}")

    asyncio.run(test_endpoints())

    print("\n" + "=" * 80)
    print("API Server Testing Complete")
    print("=" * 80)

finally:
    # Stop server
    print("\n[Cleanup] Stopping server...")
    server_process.terminate()
    server_process.wait(timeout=5)
    print("✅ Server stopped")
