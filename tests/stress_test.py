import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000"

async def send_log_request(client, i):
    payload = {
        "org_id": "org_1",
        "actor_id": f"user_{i}",
        "action": "login",
        "resource": "portal"
    }
    try:
        response = await client.post(f"{BASE_URL}/audit/log", params=payload)
        return response.status_code, response.json()
    except Exception as e:
        return 0, str(e)

async def stress_test(n=200):
    print(f"Starting stress test with {n} concurrent requests...")
    async with httpx.AsyncClient() as client:
        tasks = [send_log_request(client, i) for i in range(n)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

    success_count = sum(1 for status, _ in results if status == 200)
    fail_count = n - success_count
    
    print(f"Time taken: {end_time - start_time:.2f}s")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    
    # Analyze failures
    errors = {}
    for status, res in results:
        if status != 200:
            msg = str(res)
            errors[msg] = errors.get(msg, 0) + 1
            
    if errors:
        print("\nError breakdown:")
        for msg, count in errors.items():
            print(f"{count}x: {msg}")

if __name__ == "__main__":
    asyncio.run(stress_test())
