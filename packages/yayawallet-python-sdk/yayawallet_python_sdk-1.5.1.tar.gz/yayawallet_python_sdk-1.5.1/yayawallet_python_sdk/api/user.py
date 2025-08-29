from ..functions.api_request import api_request

from rest_framework import status

from django.http import HttpResponse

from ..serializers.user_serializers import AddOrganization, CustomerUserSerializer, BusinessUserSerializer

import json

from typing import Optional

async def get_organization(api_key = None):
  api_response = await api_request("GET", "/user/organization", "", None, api_key)
  return api_response

async def get_profile(api_key = None):
  api_response = await api_request("GET", "/user/profile", "", None, api_key)
  return api_response

async def search_profile(account_name: str, api_key: str = None):
  api_response = await api_request("POST", "/user/profile", "", { "account_name": account_name }, api_key)
  return api_response

async def search_user(query: str, api_key: str = None):
  api_response = await api_request("POST", "/user/search", "", { "query": query }, api_key)
  return api_response

async def get_balance(api_key: str = None):
  api_response = await api_request("GET", "/user/balance", "", None, api_key)
  return api_response

async def create_customer_user(data, api_key = None):
  serializer = CustomerUserSerializer(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      api_response = await api_request("POST", "/user/add-organization", "", validated_data, api_key)
      return api_response
  else:
      errors = serializer.errors
      return HttpResponse(
          json.dumps(errors),
          content_type='application/json',
          status=status.HTTP_400_BAD_REQUEST
      )

async def create_business_user(data, api_key = None):
  serializer = BusinessUserSerializer(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      api_response = await api_request("POST", "/user/register-business", "", validated_data, api_key)
      return api_response
  else:
      errors = serializer.errors
      return HttpResponse(
          json.dumps(errors),
          content_type='application/json',
          status=status.HTTP_400_BAD_REQUEST
      )

async def add_organization(data, api_key = None):
  serializer = AddOrganization(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      api_response = await api_request("POST", "/user/register", "", validated_data, api_key)
      return api_response
  else:
      errors = serializer.errors
      return HttpResponse(
          json.dumps(errors),
          content_type='application/json',
          status=status.HTTP_400_BAD_REQUEST
      )

async def update_user(api_key: str = None, **kwargs):
    payload = {
        key: value
        for key, value in kwargs.items()
        if value is not None
    }
    api_response = await api_request("POST", "/user/update", "", payload, api_key)
    return api_response

async def document_actions(action: str, document: str, account_name: str, meta_data: Optional[str] = None, api_key: str = None):
  api_response = await api_request("POST", f"/user/documents/{action}/{document}", "", { "account_name": account_name, "meta_data": meta_data  }, api_key)
  return api_response

async def send_new_pin(account_name: str, meta_data: Optional[str] = None, api_key: str = None):
  api_response = await api_request("POST", "/user/send-new-pin", "", { "account_name": account_name, "meta_data": meta_data }, api_key)
  return api_response

async def pending_approval(account_type: str, api_key: str = None):
  api_response = await api_request("POST", f"/user/pending-approval/{account_type}", "", None, api_key)
  return api_response

async def get_otp(country: str, phone: str, api_key = None):
  api_response = await api_request("POST", "/user/otp", "", {"country": country,"phone": phone}, api_key)
  return api_response


async def verify_otp(phone: str, otp: str, api_key: str = None):
    """
    Verify the OTP sent to the user's phone.

    :param phone: The phone number to verify.
    :param otp: The OTP code to verify.
    :param api_key: The API key for authentication (optional).
    :return: The API response.
    """
    payload = {
        "int_phone": phone,
        "otp": otp
    }
    api_response = await api_request("POST", "/phone-otp/verify", "", payload, api_key)
    return api_response