from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async

class DjangoModelAPISecretProvider:
    """
    Provider that fetches API secrets from a Django model
    """
    def __init__(self, model_class):
        self.model_class = model_class
    
    @sync_to_async
    def get_default_api_key(self):
        try:
            api_key_obj = self.model_class.objects.filter(is_default=True).first()
            return api_key_obj.api_key if api_key_obj else None
        except Exception as e:
            print(f"Error fetching default API key: {e}")
            return None
    
    @sync_to_async
    def get_api_secret(self, api_key: str = None) -> str:
        try:
            if api_key is None:
                # Get default API key if none provided
                api_key_obj = self.model_class.objects.filter(is_default=True).first()
            else:
                api_key_obj = self.model_class.objects.get(api_key=api_key)
            
            if not api_key_obj:
                raise ValueError("No API key found (neither specific nor default)")
                
            return api_key_obj.api_secret
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            print(f"Error fetching API secret: {e}")
            return None

# Default provider (can be set by the Django project)
_default_provider = None

def set_default_provider(provider):
    """
    Set the default provider for API secrets
    """
    global _default_provider
    _default_provider = provider

async def get_api_secret(api_key: str = None) -> str:
    """
    Get API secret using the configured provider (async version)
    """
    if _default_provider is None:
        raise RuntimeError("No API secret provider configured. "
                         "Call set_default_provider() first.")
    return await _default_provider.get_api_secret(api_key)

async def get_default_api_key() -> str:
    """
    Get default API key using the configured provider (async version)
    """
    if _default_provider is None:
        raise RuntimeError("No API secret provider configured. "
                         "Call set_default_provider() first.")
    return await _default_provider.get_default_api_key()