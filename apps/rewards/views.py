from django.conf import settings
from django.utils import timezone
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PointTransaction, Achievement, UserAchievement, WithdrawalRequest
from .serializers import (
    PointTransactionSerializer, AchievementSerializer,
    UserAchievementSerializer, WithdrawalRequestSerializer,
    WithdrawalRequestCreateSerializer,
)
from .services import PointsService, EarningsCapService, WithdrawalEligibilityService

GAME_CONFIG = settings.GAME_CONFIG


class PointsBalanceView(APIView):
    def get(self, request):
        user = request.user
        rate = GAME_CONFIG['POINTS_TO_NAIRA_RATE']
        min_wd = GAME_CONFIG['MIN_WITHDRAWAL_NAIRA']
        fee_pct = GAME_CONFIG['WITHDRAWAL_FEE_PERCENT']

        min_pts = int(min_wd / rate)
        cap_info = EarningsCapService.get_remaining_earnable(user)
        weekly_wds = WithdrawalEligibilityService.get_week_withdrawals(user)
        max_wds = GAME_CONFIG['MAX_WEEKLY_WITHDRAWALS']

        return Response({
            'total_points': user.total_points,
            'naira_equivalent': round(user.total_points * rate, 2),
            'min_withdrawal_naira': min_wd,
            'min_withdrawal_points': min_pts,
            'withdrawal_fee_percent': fee_pct,
            'can_withdraw': user.total_points >= min_pts,
            'weekly_earnings': cap_info,
            'weekly_withdrawals_used': weekly_wds,
            'weekly_withdrawals_remaining': max(0, max_wds - weekly_wds),
            'max_weekly_withdrawals': max_wds,
        })


class TransactionHistoryView(generics.ListAPIView):
    serializer_class = PointTransactionSerializer

    def get_queryset(self):
        return PointTransaction.objects.filter(user=self.request.user)


class DailyLoginBonusView(APIView):
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
    queryset = Achievement.objects.filter(is_active=True)
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserAchievementView(generics.ListAPIView):
    serializer_class = UserAchievementSerializer

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user).select_related('achievement')


class WithdrawalRequestView(APIView):
    """Submit a withdrawal request."""

    def post(self, request):
        serializer = WithdrawalRequestCreateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        wd, error = PointsService.process_withdrawal(
            user=request.user,
            amount_naira=float(data['amount_naira']),
            bank_name=data['bank_name'],
            account_number=data['account_number'],
            account_name=data['account_name'],
        )

        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        # Notify user
        try:
            from apps.notifications.utils import send_notification
            send_notification(
                request.user,
                'Withdrawal Request Submitted',
                f'Your withdrawal of ₦{wd.amount_to_receive} to '
                f'{wd.get_bank_name_display()} ({wd.account_number}) '
                f'is being processed. Ref: {wd.reference}',
                'reward',
            )
        except Exception:
            pass

        return Response({
            'message': 'Withdrawal request submitted successfully.',
            'reference': wd.reference,
            'amount_requested': str(wd.amount_requested),
            'fee': str(wd.fee_amount),
            'amount_to_receive': str(wd.amount_to_receive),
            'bank': wd.get_bank_name_display(),
            'account_number': wd.account_number,
            'account_name': wd.account_name,
            'status': wd.status,
            'new_balance': request.user.total_points,
        }, status=status.HTTP_201_CREATED)


class WithdrawalHistoryView(generics.ListAPIView):
    serializer_class = WithdrawalRequestSerializer

    def get_queryset(self):
        return WithdrawalRequest.objects.filter(user=self.request.user)


class WithdrawalBanksView(APIView):
    """Return the full list of supported banks."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        banks = [{'value': code, 'label': name}
                 for code, name in WithdrawalRequest.BANK_CHOICES]
        return Response({'banks': banks})
