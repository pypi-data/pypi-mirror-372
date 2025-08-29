from ..functions.api_request import api_request
from typing import Optional

from rest_framework import status

from django.http import HttpResponse

from ..serializers.payout_serializers import ClusterPayoutSerializer, GetPayoutSerializer

import json

async def cluster_payout(data, api_key = None):
  serializer = ClusterPayoutSerializer(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      api_response = await api_request("POST", "/payout-method/create", "", validated_data, api_key)
      return api_response
  else:
      errors = serializer.errors
      return HttpResponse(
          json.dumps(errors),
          content_type='application/json',
          status=status.HTTP_400_BAD_REQUEST
      )

async def bulk_cluster_payout(data_list, api_key = None):
  payload = []
  for data in data_list:
    serializer = ClusterPayoutSerializer(data=data)

    if serializer.is_valid():
        validated_data = serializer.validated_data
        payload.append(validated_data)
    else:
        errors = serializer.errors
        return HttpResponse(
          json.dumps(errors),
          content_type='application/json',
          status=status.HTTP_400_BAD_REQUEST,
        )

  api_response = await api_request("POST", "/bulkimport/payout-methods", "", payload, api_key)
  return api_response

async def get_payout(data, param: Optional[dict] = None, api_key: Optional[str] = None):
  serializer = GetPayoutSerializer(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      page_number_param = param or {"p": 1}
      api_response = await api_request("POST", "/payout-method/list", page_number_param, validated_data, api_key)
      return api_response
  else:
      errors = serializer.errors
      return HttpResponse(
          json.dumps(errors),
          content_type='application/json',
          status=status.HTTP_400_BAD_REQUEST
      )

async def delete_payout(id, api_key = None):
  api_response = await api_request("DELETE", "/payout-method/delete/" + id, "", None, api_key)
  return api_response