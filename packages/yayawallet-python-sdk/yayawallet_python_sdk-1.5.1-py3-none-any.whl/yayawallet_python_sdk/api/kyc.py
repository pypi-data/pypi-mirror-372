from ..functions.api_request import api_request

async def request_otp(fin, api_key = None):    
  api_response = await api_request("GET", "/kyc/fayda/request-otp/" + fin, "", None, api_key)
  return api_response

async def get_kyc_details(fin, transaction_id, otp, api_key = None):    
  api_response = await api_request("GET", "/kyc/fayda/get-kyc-details/" + fin + "/" + transaction_id + "/" + otp, "", None, api_key)
  return api_response

async def find_by_tin(tin, api_key = None):    
  api_response = await api_request("GET", "/kyc/etrade/find-by-tin/" + tin, "", None, api_key)
  return api_response

async def find_by_license_number(tin: str, licenseNumber: str, api_key: str = None):
  api_response = await api_request("POST", "/kyc/etrade/find-by-license-number/" + tin, "", {"licenseNumber": licenseNumber}, api_key)
  return api_response

async def is_registered(tin: str, license_number: str, api_key: str = None):
    payload = {
        "licenseNumber": license_number
    }
    api_response = await api_request("POST", f"/kyc/etrade/is-registered/{tin}", "", payload, api_key)
    return api_response