from rest_framework import serializers

class ClusterPayoutSerializer(serializers.Serializer):
    client_yaya_account  = serializers.CharField(required=True)
    cluster = serializers.CharField(required=True)
    bill_code = serializers.CharField(required=True)
    institution = serializers.CharField(required=True)
    account_number = serializers.CharField(required=True)
    details = serializers.JSONField(required=False)

class GetPayoutSerializer(serializers.Serializer):
    client_yaya_account  = serializers.CharField(required=False, allow_blank=True)