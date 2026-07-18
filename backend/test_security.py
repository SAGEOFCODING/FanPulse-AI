import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000"

async def run_tests():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Graceful degradation (Invalid API Key)
        print("Testing graceful degradation...")
        res = await client.post(
            f"{BASE_URL}/api/fan/chat",
            json={"message": "Hello", "accessibility_mode": False}
        )
        print(f"Chat response status: {res.status_code}")
        print(f"Chat response body: {res.text}")
        assert res.status_code == 200 # Should return 200 with fallback message
        assert "I'm experiencing a temporary issue" in res.text or "apologize" in res.text, "Fallback message not found"

        # Test 2: Endpoint resilience (Malformed JSON)
        print("\nTesting malformed JSON payload...")
        res = await client.post(
            f"{BASE_URL}/api/fan/chat",
            json={"wrong_key": "Hello"}
        )
        print(f"Malformed payload status: {res.status_code}")
        assert res.status_code == 422 # Unprocessable Entity
        assert "detail" in res.json()

        # Test 3: Endpoint resilience (Huge string)
        print("\nTesting huge string...")
        huge_string = "a" * 10000
        res = await client.post(
            f"{BASE_URL}/api/fan/chat",
            json={"message": huge_string, "accessibility_mode": False}
        )
        print(f"Huge string status: {res.status_code}")
        assert res.status_code == 422 # Assuming Pydantic catches length limit, or 400

        # Test 4: Rate Limiting
        print("\nTesting rate limits (Fan chat allowed 20/min)...")
        # Send 25 requests fast
        tasks = [client.post(f"{BASE_URL}/api/fan/chat", json={"message": f"Test {i}", "accessibility_mode": False}) for i in range(25)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        rate_limited = False
        for i, r in enumerate(responses):
            if isinstance(r, Exception):
                continue
            if r.status_code == 429:
                rate_limited = True
                print(f"Request {i+1} got 429 Too Many Requests")
                break
        assert rate_limited, "Rate limiting did not trigger!"

        # Test 5: CORS
        print("\nTesting CORS (disallowed origin)...")
        res = await client.options(
            f"{BASE_URL}/api/fan/chat",
            headers={"Origin": "https://evil-site.com", "Access-Control-Request-Method": "POST"}
        )
        print(f"CORS options status: {res.status_code}")
        # FastAPI CORS middleware returns 400 or just doesn't include the allow-origin header
        allow_origin = res.headers.get("access-control-allow-origin")
        print(f"Access-Control-Allow-Origin header: {allow_origin}")
        assert allow_origin is None, "CORS failed to block disallowed origin!"

        print("\nAll automated security and resilience tests passed!")

if __name__ == "__main__":
    asyncio.run(run_tests())
