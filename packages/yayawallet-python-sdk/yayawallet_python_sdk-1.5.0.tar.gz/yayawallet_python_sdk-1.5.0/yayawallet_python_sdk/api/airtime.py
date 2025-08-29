from ..functions.api_request import api_request

async def buy_airtime(phone: str, amount:str, api_key: str = None):
  api_response = await api_request("POST", "/airtime/buy", "", {"phone": phone, "amount": amount}, api_key)
  return api_response

async def buy_package(phone: str, package:str, api_key: str = None):
  api_response = await api_request("POST", "/airtime/buy", "", {"phone": phone, "package": package}, api_key)
  return api_response

async def list_recharges(api_key: str = None):
  api_response = await api_request("GET", "/airtime/list", "", None, api_key)
  return api_response

async def list_packages(phone: str, api_key: str = None):
  api_response = await api_request("POST", "/airtime/packages", "", {"phone": phone}, api_key)
  return api_response