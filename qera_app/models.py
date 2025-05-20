from django.db import models
from qera_user.models import User
from django.utils import timezone


class ScanHistory(models.Model):  # or rename to Product if you want
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scans')
    unique_code = models.CharField(max_length=16)
    name = models.CharField(max_length=100)
    point = models.PositiveIntegerField()
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'unique_code')  # 👈 prevents double scan by same user

    def __str__(self):
        return f"{self.user.email} - {self.unique_code}"
