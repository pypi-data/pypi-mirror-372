from ..functions.api_request import api_request
from typing import Optional

async def get_transaction_list_by_user(param: Optional[dict] = None, api_key: Optional[str] = None):
    page_number_param = param or {"p": 1}
    api_response = await api_request("GET", "/transaction/find-by-user", page_number_param, None, api_key)
    return api_response

async def create_transaction(receiver: str, amount: str, cause: str, meta_data: str, api_key: str = None):
  api_response = await api_request("POST", "/transaction/create", "", {"receiver": receiver, "amount": amount, "cause": cause, "meta_data": meta_data}, api_key)
  return api_response

async def transaction_fee(receiver: str, amount: str, api_key: str = None):
  api_response = await api_request("POST", "/transaction/fee", "", {"receiver": receiver, "amount": amount}, api_key)
  return api_response

async def generate_qr_url(amount: str, cause: str, api_key: str = None):
  api_response = await api_request("POST", "/transaction/qr-generate", "", {"amount": amount, "cause": cause}, api_key)
  return api_response

async def get_transaction_by_id(id: str, api_key: str = None):
  api_response = await api_request("GET", "/transaction/find/" + id, "", None, api_key)
  return api_response

async def search_transaction(query: str, api_key: str = None):
  api_response = await api_request("POST", "/transaction/search", "", {"query": query}, api_key)
  return api_response