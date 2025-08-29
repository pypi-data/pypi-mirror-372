import os
import httpx
import json
from typing import Dict, Optional
from django.http import HttpResponse
from yayawallet_python_sdk.functions.get_time import get_time
from yayawallet_python_sdk.functions.generate_signature import generate_signature

async def api_request(
    method: str,
    path: str,
    params: Optional[dict] = None,
    data: Optional[Dict] = None,
    api_key: Optional[str] = None,
):
    url = os.getenv("YAYA_API_URL", "") + path
    params = params or {}  # Ensure params is never None

    YAYA_API_PATH = os.getenv("YAYA_API_PATH", "") + path

    unix_time_response = await get_time()
    unix_time = str(unix_time_response['time'])

    try:
        json_body = json.dumps(data) if data is not None else ""
    except TypeError as e:
        return HttpResponse(
            json.dumps({"error": "Invalid request data format"}),
            status=400,
            content_type="application/json",
        )

    signed_payload, used_api_key = await generate_signature(
        unix_time, method, YAYA_API_PATH, json_body, api_key
    )

    headers = {
        "Content-Type": "application/json",
        "YAYA-API-KEY": used_api_key,
        "YAYA-API-TIMESTAMP": unix_time,
        "YAYA-API-SIGN": signed_payload,
    }

    try:
        async with httpx.AsyncClient(timeout=100.0) as client:
            if method == "POST":
                response = await client.post(url, params=params, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, params=params, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, params=params, headers=headers)
            else:
                response = await client.get(url, params=params, headers=headers)

            response.raise_for_status()

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("content-type", "application/json"),
            reason=response.reason_phrase
        )
    except httpx.TimeoutException as e:
        return HttpResponse(
            json.dumps({"error": "Request timed out"}),
            status=504,
            content_type="application/json"
        )
    except httpx.HTTPStatusError as e:
        return HttpResponse(
            e.response.text,
            status=e.response.status_code,
            content_type=e.response.headers.get("content-type", "application/json")
        )
    except httpx.RequestError as e:
        return HttpResponse(
            json.dumps({"error": str(e)}),
            status=502,
            content_type="application/json"
        )
    except Exception as e:
        return HttpResponse(
            json.dumps({"error": str(e)}),
            status=500,
            content_type="application/json"
        )