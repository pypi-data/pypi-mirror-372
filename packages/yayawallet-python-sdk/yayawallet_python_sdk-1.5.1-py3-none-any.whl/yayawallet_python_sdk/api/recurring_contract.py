from ..functions.api_request import api_request

async def list_all_contracts(api_key = None):
  api_response = await api_request("GET", "/recurring-contract/list", "", None, api_key)
  return api_response

async def create_contract(contract_number, service_type, customer_account_name, meta_data, api_key = None):
  api_response = await api_request("POST", "/recurring-contract/create", "", { "contract_number": contract_number, "service_type": service_type, "customer_account_name": customer_account_name, "meta_data": meta_data }, api_key)
  return api_response

async def request_payment(contract_number, amount, currency, cause, notification_url, meta_data, api_key = None):
  api_response = await api_request("POST", "/recurring-contract/request-payment", "", { "contract_number": contract_number, "amount": amount,  "currency": currency,"cause": cause,"notification_url": notification_url,"meta_data": meta_data,}, api_key)
  return api_response

async def get_subscriptions(api_key = None):
  api_response = await api_request("GET", "/recurring-contract/subscriptions", "", None, api_key)
  return api_response

async def get_list_of_payment_requests(api_key = None):
  api_response = await api_request("GET", "/recurring-contract/payment-requests", "", None, api_key)
  return api_response

async def approve_payment_request(id, api_key = None):
  api_response = await api_request("GET", "/recurring-contract/approve-payment/" + id, "", None, api_key)
  return api_response

async def reject_payment_request(id, api_key = None):
  api_response = await api_request("GET", "/recurring-contract/reject-payment/" + id, "", None, api_key)
  return api_response

async def activate_subscription(id, api_key = None):
  api_response = await api_request("GET", "/recurring-contract/activate/" + id, "", None, api_key)
  return api_response

async def deactivate_subscription(id, api_key = None):
  apiResponse = await api_request("GET", "/recurring-contract/deactivate/" + id, "", None, api_key)
  return apiResponse