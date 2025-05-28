from rest_framework import serializers
from .models import ScanHistory  # or Product if you renamed it
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_id', 'amount', 'points_used', 'status', 'created_at']
        read_only_fields = ['id', 'transaction_id', 'created_at']
class ScanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanHistory
        fields = ['id', 'unique_code', 'name', 'point', 'scanned_at']
        read_only_fields = ['id', 'scanned_at']
