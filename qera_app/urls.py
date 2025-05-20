from rest_framework.routers import DefaultRouter
from  django.urls import path, include
from .views import ScanViewSet, ScanHistoryViewSet


router = DefaultRouter()
router.register(r'product_qr', ScanViewSet, basename='scan')
router.register(r'', ScanHistoryViewSet, basename=' ')

urlpatterns = [
    path('', include(router.urls)),
]