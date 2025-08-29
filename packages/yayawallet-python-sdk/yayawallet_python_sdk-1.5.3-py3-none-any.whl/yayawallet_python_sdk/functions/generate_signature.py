import hashlib
import hmac
import base64
from yayawallet_python_sdk.functions.get_api_secret import get_api_secret, get_default_api_key

async def generate_signature(timestamp, method, endpoint, body, api_key=None):
    prehash_string = timestamp + method + endpoint + body
    
    # If no API key provided, get the default one
    if api_key is None:
        api_key = await get_default_api_key()
        if api_key is None:
            raise ValueError("No API key provided and no default API key found")
    
    api_secret = await get_api_secret(api_key)
    
    if api_secret is None:
        raise ValueError(f"API secret not found for API key: {api_key}")
        
    hashed_key = hmac.new(
        bytes(api_secret, 'UTF-8'), 
        msg=bytes(prehash_string, 'UTF-8'), 
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(hashed_key).decode()
    return signature, api_key  # Return both signature and the api_key used