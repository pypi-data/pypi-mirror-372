from ..functions.api_request import api_request

async def gender_lookup(api_key = None):
  api_response = await api_request("GET", "/lookup/gender", "", None, api_key)
  return api_response

async def region_lookup(api_key = None):
  api_response = await api_request("GET", "/lookup/region", "", None, api_key)
  return api_response

async def business_categories_lookup(api_key = None):
  api_response = await api_request("GET", "/lookup/business-categories", "", None, api_key)
  return api_response