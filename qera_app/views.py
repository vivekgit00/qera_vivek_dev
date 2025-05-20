from .models import ScanHistory
from .serializers import ScanHistorySerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db.models import Sum
from qera_user.models import User
from utils import custom_response

class ScanViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='scan')
    def scan_qr(self, request):
        serializer = ScanHistorySerializer(data=request.data)
        if not serializer.is_valid():
            return custom_response(
                message="Invalid scan data",
                status=0,
                data=serializer.errors
            )

        unique_code = serializer.validated_data['unique_code']

        if ScanHistory.objects.filter(user=request.user, unique_code=unique_code).exists():
            return custom_response(
                message="You already scanned this QR code.",
                status=0
            )

        scan = serializer.save(user=request.user)

        total_points = request.user.scans.aggregate(total=Sum('point'))['total'] or 0

        return custom_response(
            message="QR Code scanned successfully!",
            status=1,
            data={
                "points_received": scan.point,
                "total_points": total_points,
                "scan": ScanHistorySerializer(scan).data
            }
        )
class ScanHistoryViewSet(viewsets.ModelViewSet):
    queryset = ScanHistory.objects.all()
    serializer_class = ScanHistorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='leaderboard', permission_classes=[])
    def leaderboard(self, request):
        users = (
            User.objects
            .annotate(total_points=Sum('scans__point'))
            .filter(total_points__isnull=False)
            .order_by('-total_points')
        )

        data = [
            {
                'rank': idx + 1,
                'name': user.name,
                'email': user.email,
                'total_points': user.total_points
            }
            for idx, user in enumerate(users)
        ]

        return custom_response(
            message="Leaderboard fetched successfully",
            status=1,
            data=data
        )