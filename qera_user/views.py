from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .models import User
from .serialzers import RegisterSerialzer
from rest_framework.response import Response
from utils import custom_response



class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerialzer

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return custom_response(
                message="Registered successfully",
                status=1,
                data={"token": token.key, "user": serializer.data}
            )
        return custom_response(message="Validation failed", status=0, data=serializer.errors)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = User.objects.get(email=email)
            if user.otp != otp:
                return custom_response(message="Invalid OTP", status=0)

            if timezone.now() - user.otp_created_at > timedelta(minutes=10):
                return custom_response(message="OTP expired", status=0)

            user.otp_verified = True
            user.otp = None
            user.save()
            return custom_response(message="OTP verified successfully", status=1)
        except User.DoesNotExist:
            return custom_response(message="User not found", status=0)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()

        if not email or not password:
            return custom_response(message="Email and password are required", status=0)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return custom_response(message="User not found", status=0)

        if not user.check_password(password):
            return custom_response(message="Invalid credentials", status=0)

        if not user.otp_verified:
            return custom_response(message="User not verified. Please verify OTP first.", status=0)

        token, _ = Token.objects.get_or_create(user=user)
        return custom_response(
            message="Login successful",
            status=1,
            data={"token": token.key}
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='change_password')
    def change_password(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        user.set_password(new_password)
        user.save()
        return custom_response(message="Password changed successfully", status=1)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='update_profile')
    def update_profile(self, request):
        user = request.user
        allowed_fields = ['name', 'city', 'state', 'address1', 'address2', "pincode", 'country']
        update_data = {field: value for field, value in request.data.items() if field in allowed_fields}

        serializer = self.get_serializer(user, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return custom_response(message="Profile updated", status=1, data=serializer.data)
        return custom_response(message="Update failed", status=0, data=serializer.errors)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='logout')
    def logout(self, request):
        try:
            token = request.auth
            token.delete()
            return custom_response(message="Logged out successfully", status=1)
        except Exception as e:
            return custom_response(message=f"Logout failed: {str(e)}", status=0)
