from rest_framework import serializers
from .models import User
import random
from django.utils import timezone


class RegisterSerialzer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'state', 'city', 'password']

    
    def create(self, validated_data):
        password = validated_data.pop('password')
        otp = str(random.randint(100000, 999999))
        user = User(**validated_data)
        user.set_password(password)
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        print(f'OTP for {user.email} is {otp}')
        return user

        
