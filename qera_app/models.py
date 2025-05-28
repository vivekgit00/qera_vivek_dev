from django.db import models
from qera_user.models import User
from django.utils import timezone
import uuid


class ScanHistory(models.Model):  # or rename to Product if you want
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scans')
    unique_code = models.CharField(max_length=16)
    name = models.CharField(max_length=100)
    point = models.PositiveIntegerField()
    points_used = models.PositiveIntegerField(default=0)
    scanned_at = models.DateTimeField(auto_now_add=True)
    is_scanned = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'unique_code')  # 👈 prevents double scan by same user

    def __str__(self):
        return f"{self.user.email} - {self.unique_code}"

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    points_used = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        ordering = ['-created_at']
        db_table = 'transactions'
        
        
    def __str__(self):
        return f"{self.user.email} - ₹{self.amount} - {self.status}"