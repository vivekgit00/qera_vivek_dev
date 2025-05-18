from rest_framework.routers import DefaultRouter
from  django.urls import path, include
from .views import ProductView


router = DefaultRouter()
router.register(r'product', ProductView, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]