from rest_framework import serializers
from .models import ScanHistory  # or Product if you renamed it

class ScanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanHistory
        fields = ['id', 'unique_code', 'name', 'point', 'scanned_at']
        read_only_fields = ['id', 'scanned_at']
