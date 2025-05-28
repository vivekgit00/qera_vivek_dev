from .models import ScanHistory
from .serializers import ScanHistorySerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db.models import Sum
from .models import User
from .models import Transaction
from .serializers import TransactionSerializer
from utils import custom_response
from django.db.models import Sum, F, ExpressionWrapper, IntegerField
from django.db.models.functions import Coalesce

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
        if ScanHistory.objects.filter(unique_code=unique_code, is_scanned=True).exists():
            return custom_response(
                message="This QR code has already been used.",
                status=0
            )

        scan = serializer.save(user=request.user, is_scanned=True)

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
            .annotate(
                total_earned=Coalesce(Sum('scans__point'), 0),
                total_used=Coalesce(Sum('scans__points_used'), 0)
            )
            .annotate(
                total_points=ExpressionWrapper(
                    F('total_earned') - F('total_used'),
                    output_field=IntegerField()
                )
            )
            .filter(total_points__gt=0)  # optional: show only users with points
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
    @action(detail=False, methods=['get'], url_path='point-history', permission_classes=[IsAuthenticated])
    def point_history(self, request):
        user = request.user
        print(user)
        history = ScanHistory.objects.filter(user=user).order_by('-scanned_at')
        serializer = ScanHistorySerializer(history, many=True)

        return custom_response(
            message="Point history fetched successfully",
            status=1,
            data=serializer.data
        )
        

class TransactionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='history')
    def transaction_history(self, request):
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return custom_response(
            message="Transaction history fetched successfully",
            status=1,
            data=serializer.data
        )
    @action(detail=False, methods=['post'], url_path='create')
    def create_transaction(self, request):
        user = request.user
        amount = request.data.get('amount')

        # Validate amount
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return custom_response("Invalid amount", 0)

        if amount <= 0:
            return custom_response("Amount must be greater than 0", 0)

        # Check available points
        total_points = user.scans.aggregate(total=Sum('point'))['total'] or 0
        used_points = user.scans.aggregate(used=Sum('points_used'))['used'] or 0
        available_points = total_points - used_points

        if amount > available_points:
            return custom_response("Insufficient points", 0)

        # Deduct points FIFO from ScanHistory
        remaining = amount
        scans = ScanHistory.objects.filter(user=user).order_by('scanned_at')

        for scan in scans:
            available = scan.point - scan.points_used
            if available <= 0:
                continue

            if remaining <= available:
                scan.points_used += remaining
                scan.save()
                break
            else:
                scan.points_used = scan.point
                scan.save()
                remaining -= available


        # Create and confirm transaction
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            points_used=amount,
            status='confirmed'  # ✅ mark as confirmed directly
        )

        serializer = TransactionSerializer(transaction)

        return custom_response(
            message="Transaction successful & points deducted",
            status=1,
            data=serializer.data
        )