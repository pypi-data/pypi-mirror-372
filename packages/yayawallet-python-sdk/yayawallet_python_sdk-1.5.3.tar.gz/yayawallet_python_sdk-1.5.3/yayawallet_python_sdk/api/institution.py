from ..functions.api_request import api_request

async def list_institution(country: str, api_key = None):
  api_response = await api_request("POST", "/financial-institution/list", "", {"country": country}, api_key)
  return api_response