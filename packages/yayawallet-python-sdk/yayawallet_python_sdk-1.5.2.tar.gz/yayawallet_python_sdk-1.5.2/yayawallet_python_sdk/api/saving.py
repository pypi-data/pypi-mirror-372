from ..functions.api_request import api_request

async def create_saving(amount: str, action: str = "deposit", api_key = None):
  api_response = await api_request("POST", "/saving/create", "", {"amount": amount, "action": action}, api_key)
  return api_response

async def withdraw_saving(api_key = None):
  api_response = await api_request("GET", "/saving/withdrawals", "", None, api_key)
  return api_response

async def claim(request_ids, api_key = None):
  api_response = await api_request("POST", "/saving/refund", "", {"request_ids": request_ids}, api_key)
  return api_response