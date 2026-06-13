from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, ReferralReward


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirm password')
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'password2', 'referral_code']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        validated_data.pop('password2')

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        if referral_code:
            try:
                referrer = CustomUser.objects.get(referral_code=referral_code)
                user.referred_by = referrer
                user.save(update_fields=['referred_by'])
                # Create pending referral reward
                ReferralReward.objects.create(referrer=referrer, referred_user=user)
            except CustomUser.DoesNotExist:
                pass  # Invalid referral code — silently ignore

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    level_name = serializers.ReadOnlyField()
    accuracy_rate = serializers.ReadOnlyField()
    referral_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'bio', 'country', 'phone_number',
            'total_points', 'total_xp', 'level', 'level_name',
            'referral_code', 'current_streak', 'longest_streak',
            'total_games_played', 'total_correct_answers',
            'total_wrong_answers', 'total_challenges_won',
            'total_withdrawn_naira', 'accuracy_rate',
            'referral_count', 'is_email_verified', 'date_joined',
        ]
        read_only_fields = [
            'id', 'email', 'total_points', 'total_xp', 'level',
            'referral_code', 'current_streak', 'longest_streak',
            'total_games_played', 'total_correct_answers',
            'total_wrong_answers', 'total_challenges_won',
            'total_withdrawn_naira', 'is_email_verified', 'date_joined',
        ]

    def get_referral_count(self, obj):
        return obj.referrals.count()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'bio', 'country', 'phone_number', 'avatar']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return attrs


class TopperTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer — adds user data to token response."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['level'] = user.level
        token['total_points'] = user.total_points
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user.update_streak()
        data['user'] = UserProfileSerializer(user).data
        return data


class ReferralRewardSerializer(serializers.ModelSerializer):
    referred_user_username = serializers.CharField(source='referred_user.username', read_only=True)

    class Meta:
        model = ReferralReward
        fields = ['id', 'referred_user_username', 'points_awarded', 'bonus_naira', 'status', 'created_at', 'paid_at']


class PublicUserSerializer(serializers.ModelSerializer):
    """Minimal public-facing user data."""
    level_name = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar', 'level', 'level_name', 'total_points', 'country']
