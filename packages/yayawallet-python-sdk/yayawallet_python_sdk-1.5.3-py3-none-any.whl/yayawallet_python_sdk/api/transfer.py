from ..functions.api_request import api_request
from typing import Optional

async def get_transfer_list(param: Optional[dict] = None, api_key: Optional[str] = None):
  page_number_param = param or {"p": 1}
  api_response = await api_request("GET", "/transfer/list", page_number_param, None, api_key)
  return api_response

async def transfer_as_user(institution_code: str, account_number: str, amount: str, ref_code: str, sender_note: str, phone: str, api_key: str = None):
  api_response = await api_request("POST", "/transfer/send", "", {"institution_code": institution_code, "account_number": account_number, "amount": amount, "ref_code": ref_code, "sender_note": sender_note, "phone": phone}, api_key)
  return api_response

async def external_account_lookup(institution_code: str, account_number: str, api_key: str = None):
  api_response = await api_request("POST", "/transfer/lookup-external", "", {"institution_code": institution_code, "account_number": account_number}, api_key)
  return api_response

async def get_transfer_fee(institution_code: str, amount: str, api_key: str = None):
  api_response = await api_request("POST", "/transfer/fee", "", {"institution_code": institution_code, "amount": amount}, api_key)
  return api_response