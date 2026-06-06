from rest_framework import serializers
from django.conf import settings
from .models import PointTransaction, Achievement, UserAchievement, AirtimeRedemption

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


class RedeemAirtimeSerializer(serializers.Serializer):
    network = serializers.ChoiceField(choices=['mtn', 'airtel', 'glo', '9mobile'])
    phone_number = serializers.CharField(min_length=11, max_length=14)
    points_to_redeem = serializers.IntegerField(min_value=GAME_CONFIG['MIN_REDEMPTION_POINTS'])

    def validate_points_to_redeem(self, value):
        user = self.context['request'].user
        if value > user.total_points:
            raise serializers.ValidationError('Insufficient points.')
        return value

    def validate_phone_number(self, value):
        cleaned = value.replace(' ', '').replace('-', '')
        if not cleaned.isdigit():
            raise serializers.ValidationError('Phone number must contain only digits.')
        return cleaned


class AirtimeRedemptionSerializer(serializers.ModelSerializer):
    network_display = serializers.CharField(source='get_network_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AirtimeRedemption
        fields = [
            'id', 'network', 'network_display', 'phone_number',
            'points_used', 'naira_value', 'status', 'status_display',
            'created_at', 'processed_at',
        ]
