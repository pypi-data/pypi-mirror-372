from ..functions.api_request import api_request
from typing import Optional

async def get_utilities_list(api_key: Optional[str] = None):
    """
    Fetches the list of utilities.

    :param api_key: Optional API key for authentication.
    :return: API response.
    """
    api_response = await api_request("GET", "/utilities/list", "", None, api_key)
    return api_response