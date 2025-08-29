from rest_framework import serializers

class CustomerUserSerializer(serializers.Serializer):
    invitation_hash = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.IntegerField(required=False)
    region = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    account_name = serializers.CharField(required=False, allow_blank=True)
    fin = serializers.CharField(required=False, allow_blank=True)
    photo_base64 = serializers.CharField(required=True)
    id_front_base64 = serializers.CharField(required=True)
    id_back_base64 = serializers.CharField(required=True)
    meta_data = serializers.JSONField(required=False)

    def validate(self, data):
        if not data.get('invitation_hash') and not data.get('fin'):
            raise serializers.ValidationError("Either invitation_hash or fin must be provided.")
        return data

class BusinessUserSerializer(serializers.Serializer):
    invitation_hash = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.IntegerField(required=False)
    country = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    otp = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    account_name = serializers.CharField(required=False, allow_blank=True)
    trade_name = serializers.CharField(required=False, allow_blank=True)
    mcc = serializers.CharField(required=False, allow_blank=True)
    fin = serializers.CharField(required=False, allow_blank=True)
    photo_base64 = serializers.CharField(required=True)
    id_front_base64 = serializers.CharField(required=True)
    id_back_base64 = serializers.CharField(required=True)
    tin_number = serializers.CharField(required=False, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_blank=True)
    tin_doc_base64 = serializers.CharField(required=False, allow_blank=True)
    license_doc_base64 = serializers.CharField(required=False, allow_blank=True)
    logo_base64 = serializers.CharField(required=False, allow_blank=True)
    vat_number = serializers.CharField(required=False, allow_blank=True)
    meta_data = serializers.JSONField(required=False)

    def validate(self, data):
        if not data.get('invitation_hash') and not data.get('fin'):
            raise serializers.ValidationError("Either invitation_hash or fin must be provided.")
        return data

class AddOrganization(serializers.Serializer):
    account_name = serializers.CharField(required=False, allow_blank=True)
    trade_name = serializers.CharField(required=False, allow_blank=True)
    tin_number = serializers.CharField(required=True)
    license_number = serializers.CharField(required=True)
    vat_number = serializers.CharField(required=False, allow_blank=True)
    meta_data = serializers.JSONField(required=False)

    def validate(self, data):
        return data