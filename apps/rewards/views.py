from django.conf import settings
from django.utils import timezone
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PointTransaction, Achievement, UserAchievement, AirtimeRedemption
from .serializers import (
    PointTransactionSerializer, AchievementSerializer,
    UserAchievementSerializer, RedeemAirtimeSerializer,
    AirtimeRedemptionSerializer,
)
from .services import PointsService

GAME_CONFIG = settings.GAME_CONFIG


class PointsBalanceView(APIView):
    def get(self, request):
        user = request.user
        rate = GAME_CONFIG['POINTS_TO_NAIRA_RATE']
        min_pts = GAME_CONFIG['MIN_REDEMPTION_POINTS']
        return Response({
            'total_points': user.total_points,
            'naira_equivalent': round(user.total_points * rate, 2),
            'min_redemption_points': min_pts,
            'min_redemption_naira': round(min_pts * rate, 2),
            'can_redeem': user.total_points >= min_pts,
        })


class TransactionHistoryView(generics.ListAPIView):
    serializer_class = PointTransactionSerializer

    def get_queryset(self):
        return PointTransaction.objects.filter(user=self.request.user)


class DailyLoginBonusView(APIView):
    """Claim the daily login bonus."""
    def post(self, request):
        bonus = PointsService.award_daily_login_bonus(request.user)
        if bonus is None:
            return Response({'message': 'Daily bonus already claimed today.', 'already_claimed': True})
        return Response({
            'message': f'Daily bonus claimed! +{bonus} points.',
            'points_awarded': bonus,
            'new_balance': request.user.total_points,
            'current_streak': request.user.current_streak,
        })


class AchievementListView(generics.ListAPIView):
    """All platform achievements."""
    queryset = Achievement.objects.filter(is_active=True)
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserAchievementView(generics.ListAPIView):
    """Achievements earned by the authenticated user."""
    serializer_class = UserAchievementSerializer

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user).select_related('achievement')


class RedeemAirtimeView(APIView):
    """Redeem points for airtime."""
    def post(self, request):
        serializer = RedeemAirtimeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        rate = GAME_CONFIG['POINTS_TO_NAIRA_RATE']
        points = data['points_to_redeem']
        naira_value = round(points * rate, 2)

        # Deduct points
        PointsService.deduct_points(
            user=user,
            amount=points,
            transaction_type=PointTransaction.TYPE_REDEEMED,
            description=f'Airtime redemption – ₦{naira_value} to {data["phone_number"]}',
        )

        redemption = AirtimeRedemption.objects.create(
            user=user,
            network=data['network'],
            phone_number=data['phone_number'],
            points_used=points,
            naira_value=naira_value,
        )

        # Update user's airtime earned total
        user.total_airtime_earned += naira_value
        user.save(update_fields=['total_airtime_earned'])

        return Response({
            'message': 'Redemption request submitted. Airtime will be sent shortly.',
            'redemption_id': str(redemption.id),
            'naira_value': str(naira_value),
            'points_used': points,
            'new_balance': user.total_points,
            'status': redemption.status,
        }, status=status.HTTP_201_CREATED)


class AirtimeHistoryView(generics.ListAPIView):
    serializer_class = AirtimeRedemptionSerializer

    def get_queryset(self):
        return AirtimeRedemption.objects.filter(user=self.request.user)
