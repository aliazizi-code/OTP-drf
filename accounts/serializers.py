from rest_framework import serializers

from accounts.models import OTPRequest


class OTPRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPRequest
        fields = ('phone', 'request_id')
        read_only_fields = ('request_id',)


class VerifyOTPRequestSerializer(serializers.Serializer):
    request_id = serializers.CharField()
    password = serializers.CharField(max_length=6)
    phone = serializers.CharField(max_length=20)


class ObtainTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128)
    refresh = serializers.CharField(max_length=128)
    created = serializers.BooleanField()
