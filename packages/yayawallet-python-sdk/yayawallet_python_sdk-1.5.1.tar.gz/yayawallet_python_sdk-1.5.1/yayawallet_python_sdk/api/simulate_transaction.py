from ..functions.api_request import api_request
from typing import Optional


async def create_simulated_transaction(institution: str, bill_id: str, forward_transfer_ref: str, api_key: str = None):
  api_response = await api_request("POST", "/simulated-transactions", "", {"institution": institution, "bill_id": bill_id, "forward_transfer_ref": forward_transfer_ref}, api_key)
  return api_response

async def create_bulk_simulated_transaction( transactions, api_key: str = None):
  api_response = await api_request(
      "POST",
      "/bulkimport/simulated-transactions",
      transactions,
      api_key
  )
  return api_response

async def check_bulk_status(param: Optional[dict] = None, api_key: Optional[str] = None):
  param = param or {}

  if hasattr(param, 'dict'):
    param = param.dict()

  api_response = await api_request("GET", "/bulkimport", param, None, api_key)
  return api_response

async def bulk_status_details(uuid: str, api_key: Optional[str] = None):
  api_response = await api_request("GET", f"/bulkimport/{uuid}", None, None, api_key)
  return api_response

async def update_simulated_transaction(bill_id: str, transaction: dict, api_key: str = None):
  api_response = await api_request("PUT", f"/simulated-transactions/{bill_id}", "", transaction, api_key)
  return api_response

async def get_simulated_transaction(transaction_id: str, api_key: str = None):
  api_response = await api_request("GET", "/simulated-transactions/" + transaction_id, "", None, api_key)
  return api_response

async def list_simulated_transactions(param: Optional[dict] = None, api_key: Optional[str] = None):
    if param is None:
      param = {}

    if hasattr(param, 'dict'):
      param = param.dict()

    api_response = await api_request("GET", "/simulated-transactions", param, None, api_key)
    return api_response

async def  get_pending_verification_transfers(param: Optional[dict] = None, api_key: Optional[str] = None):
    if param is None:
      param = {}

    if hasattr(param, 'dict'):
      param = param.dict()

    api_response = await api_request("GET", "/admin/simulated-transfer/pending-verification", param, None, api_key)
    return api_response

async def update_simulated_transfer(simulated_transaction_id: str, valid_ref_num: str, channel: str, api_key: str = None):
  api_response = await api_request("POST", "/admin/simulated-transfer/update", "", {"simulated_transaction_id": simulated_transaction_id, "valid_ref_num": valid_ref_num, "channel": channel}, api_key)
  return api_response