from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from . import serializers
from .custom_throttle import MinuteThrottle, DayThrottle
from .models import OTPRequest, User
from .sender import send_otp


class OTPRequestView(APIView):
    throttle_classes = (MinuteThrottle, DayThrottle)

    def get(self, request: Request):
        serializer = serializers.OTPRequestSerializer(data=request.query_params)

        if serializer.is_valid():
            data = serializer.validated_data
            otp_request, created = OTPRequest.objects.get_or_create(phone=data['phone'])
            otp_request.refresh_otp() if not created else None
            send_otp(otp_request.password)
            return Response(
                data={'request_id': otp_request.request_id},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    def post(self, request: Request):
        serializer = serializers.VerifyOTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            otp_request: OTPRequest = OTPRequest()
            if otp_request.is_valid(data):
                return Response(self._handle_login(data), status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def _handle_login(self, otp):
        query = User.objects.filter(phone_number=otp['phone'])
        if query.exists():
            created = False
            user = query.first()

        else:
            created = True
            user = User.objects.create(phone_number=otp['phone'])

        refresh = RefreshToken.for_user(user)

        return serializers.ObtainTokenSerializer({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'created': created
        }).data
