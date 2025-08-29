import hashlib
import hmac
import base64
import time
from yayawallet_python_sdk.functions.get_api_secret import get_api_secret

def get_verified_payment_details(data: dict, signature):
    if verify_signature(data, signature):
        return {
            "amount": data["amount"],
            "yaya_id": data["id"],
            "currency": data["currency"],
            "cause": data["cause"],
            "full_name": data["full_name"],
            "account_name": data["account_name"],
            "invoice_url": data["invoice_url"]
        }
    return False

def verify_signature(data, signature):
    time_stamp_expiry = 300
    api_secret = get_api_secret()
    
    if api_secret is None:
        return False
        
    data_values = data.values()
    prehash_string = "".join(str(v) for v in data_values)
    hashed_key = hmac.new(bytes(api_secret, 'UTF-8'), msg=bytes(prehash_string, 'UTF-8'), digestmod=hashlib.sha256).digest()
    signed_payload = base64.b64encode(hashed_key).decode()
    
    current_unix = time.time()

    if (signed_payload == signature and current_unix - data["timestamp"] <= time_stamp_expiry):
        return True
    return False