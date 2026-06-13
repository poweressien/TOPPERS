from decimal import Decimal
from rest_framework import serializers
from django.conf import settings
from .models import PointTransaction, Achievement, UserAchievement, WithdrawalRequest

GAME_CONFIG = settings.GAME_CONFIG


class PointTransactionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = PointTransaction
        fields = ['id', 'amount', 'transaction_type', 'type_display', 'description', 'balance_after', 'created_at']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'badge_emoji', 'achievement_type', 'threshold', 'points_reward']


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'earned_at']


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    bank_display = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WithdrawalRequest
        fields = [
            'id', 'reference', 'bank_name', 'bank_display',
            'account_number', 'account_name',
            'amount_requested', 'fee_amount', 'amount_to_receive',
            'points_deducted', 'status', 'status_display',
            'rejection_reason', 'created_at', 'processed_at',
        ]
        read_only_fields = [
            'id', 'reference', 'fee_amount', 'amount_to_receive',
            'points_deducted', 'status', 'rejection_reason',
            'created_at', 'processed_at',
        ]


class WithdrawalRequestCreateSerializer(serializers.Serializer):
    amount_naira   = serializers.DecimalField(max_digits=10, decimal_places=2,
                                              min_value=Decimal(str(GAME_CONFIG['MIN_WITHDRAWAL_NAIRA'])))
    bank_name      = serializers.ChoiceField(choices=[b[0] for b in WithdrawalRequest.BANK_CHOICES])
    account_number = serializers.CharField(min_length=10, max_length=20)
    account_name   = serializers.CharField(min_length=3, max_length=200)

    def validate_account_number(self, value):
        cleaned = value.strip().replace(' ', '')
        if not cleaned.isdigit():
            raise serializers.ValidationError('Account number must contain only digits.')
        return cleaned

    def validate_amount_naira(self, value):
        request = self.context.get('request')
        if not request:
            return value
        user = request.user
        rate = GAME_CONFIG['POINTS_TO_NAIRA_RATE']
        points_needed = int(float(value) / rate)
        if user.total_points < points_needed:
            raise serializers.ValidationError(
                f'Insufficient points. You need {points_needed:,} pts for ₦{value:,}.'
            )
        return value
