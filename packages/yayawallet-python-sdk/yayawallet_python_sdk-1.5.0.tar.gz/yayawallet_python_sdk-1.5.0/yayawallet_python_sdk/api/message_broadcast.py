from ..functions.api_request import api_request

async def send_email(obj, api_key: str = None):
  api_response = await api_request("POST", "/email", "", obj, api_key)
  return api_response

async def send_sms(obj, api_key: str = None):
  api_response = await api_request("POST", "/sms", "", obj, api_key)
  return api_response

async def send_direct_sms(obj, api_key: str = None):
  api_response = await api_request("POST", "/sms-direct", "", obj, api_key)
  return api_response

async def push_app_notification(obj, api_key: str = None):
  api_response = await api_request("POST", "/app-notification", "", obj, api_key)
  return api_response

async def get_aliases(api_key: str = None):
    """
    Fetches the list of available user aliases/categories from the Yaya Wallet API.

    Args:
        api_key (str, optional): The API key for authentication. Defaults to None.

    Returns:
        dict: A dictionary mapping alias keys to their descriptions.
               Example:
               {
                   "all": "All active users",
                   "level1": "Level 1 users",
                   ...
               }
    """
    api_response = await api_request("GET", "/aliases", "", None, api_key)
    return api_response