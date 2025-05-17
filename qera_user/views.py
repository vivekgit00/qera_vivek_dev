from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated  
from rest_framework.response import Response
from rest_framework import status
from .serialzers import RegisterSerialzer, User
from  rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action



class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerialzer
    # permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'data': serializer.data, 'status':status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = User.objects.get(email=email)
            if user.otp != otp:
                return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if OTP is expired (e.g., valid for 10 minutes)
            if timezone.now() - user.otp_created_at > timedelta(minutes=10):
                return Response({'detail': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)

            user.otp_verified = True
            user.otp = None  # Optional: Clear OTP after verification
            user.save()
            return Response({'detail': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        email = request.data.get('email').strip()
        password = request.data.get('password').strip()
        print(email, password)
        if not email or not password:
            return Response({'error': 'email number and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.check_password(password):
            return Response({"error": "Invalid email number or password."},
                            status=status.HTTP_401_UNAUTHORIZED)


        if not user.otp_verified:
            return Response({"error": "User not verified. Please verify OTP first."},
                            status=status.HTTP_403_FORBIDDEN)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful",
            "token": token.key
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='change_password')
    def change_password(self, request):
        user = request.user
        # old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        print(new_password)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='update_profile')
    def update_profile(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='logout')
    def logout(self, request):
        try:
            token = request.auth
            token.delete()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
