from rest_framework import serializers
from .models import User
import random
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


class RegisterSerialzer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'state', 'city', 'password', 'address1', 'address2', 'pincode', 'country', "otp_verified"]

    def validate_email(self, value):
        return value.lower()
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        otp = str(random.randint(100000, 999999))
        user = User(**validated_data)
        user.set_password(password)
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        print(f'OTP for {user.email} is {otp}')
        send_mail(
            subject='Your OTP for registration',
            message=f'Your OTP is {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False
        )
        return user


    

        
