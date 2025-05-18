from django.db import models


class Product(models.Model):
    unique_code = models.CharField(max_length=16, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    activated = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

