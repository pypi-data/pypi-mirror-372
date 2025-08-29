from ..functions.api_request import api_request
from typing import Optional

async def create(institution_code: str, account_number: str, amount: str, reason: str, recurring: str, start_at: str, meta_data, api_key: str = None):
  api_response = await api_request("POST", "/scheduled-payment/create", "", {"institution_code": institution_code, "account_number": account_number, "amount": amount, "reason": reason, "recurring": recurring, "start_at": start_at, "meta_data": meta_data}, api_key)
  return api_response

async def get_list(param: Optional[dict] = None, api_key: Optional[str] = None):
  page_number_param = param or {"p": 1}
  api_response = await api_request("GET", "/scheduled-payment/list", page_number_param, None, api_key)
  return api_response

async def archive(id, api_key = None):
  api_response = await api_request("GET", "/scheduled-payment/archive/" + id, "", None, api_key)
  return api_response