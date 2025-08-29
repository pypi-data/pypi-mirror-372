import os
import httpx
import json

async def get_time():
    url = os.getenv("YAYA_API_URL") + '/time'
    try:
        response = httpx.get(url, timeout=100.0)
        response.raise_for_status()
        return json.loads(response.text)
    except httpx.HTTPError as exc:
        print(f"HTTP Exception for {exc.request.url} - {exc}")
        raise