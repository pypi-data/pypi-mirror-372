from ..functions.api_request import api_request

async def find_by_inviter(api_key = None):
  api_response = await api_request("GET", "/invitation/find-by-inviter", "", None, api_key)
  return api_response

async def create_inivitation(country: str, phone: str, amount: str, api_key = None):
  api_response = await api_request("POST", "/invitation/create", "", {"country": country,"phone": phone,"amount": amount}, api_key)
  return api_response

async def verify_invitation(invite_hash: str, api_key = None):
  api_response = await api_request("POST", "/invitation/find-by-hash", "", {"invite_hash": invite_hash}, api_key)
  return api_response

async def cancel_invite(invite_hash: str, api_key = None):
  api_response = await api_request("DELETE", "/invitation/cancel/" + invite_hash, "", None, api_key)
  return api_response

async def get_otp_legacy(country: str, phone: str, invite_hash: str, api_key = None):
  api_response = await api_request("POST", "/invitation/otp", "", {"country": country,"phone": phone,"invite_hash": invite_hash}, api_key)
  return api_response