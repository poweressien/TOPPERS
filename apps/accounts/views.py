from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, ReferralReward
from .serializers import (
    RegisterSerializer, UserProfileSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, TopperTokenObtainPairSerializer,
    ReferralRewardSerializer, PublicUserSerializer,
)

User = get_user_model()


# ─── Auth Views ───────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Issue tokens on registration
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Registration successful.',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = TopperTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully.'})


# ─── User Profile Views ───────────────────────────────────────

class MeView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer


class PublicProfileView(generics.RetrieveAPIView):
    """Public profile view — visible to all authenticated users."""
    queryset = User.objects.filter(is_active=True)
    serializer_class = PublicUserSerializer
    lookup_field = 'username'


class UserStatsView(APIView):
    """Detailed stats for the authenticated user."""
    def get(self, request):
        user = request.user
        return Response({
            'total_games': user.total_games_played,
            'correct_answers': user.total_correct_answers,
            'wrong_answers': user.total_wrong_answers,
            'accuracy_rate': user.accuracy_rate,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'challenges_won': user.total_challenges_won,
            'total_points': user.total_points,
            'total_xp': user.total_xp,
            'level': user.level,
            'level_name': user.level_name,
            'total_withdrawn_naira': str(user.total_withdrawn_naira),
        })


# ─── Referral Views ───────────────────────────────────────────

class ReferralDashboardView(APIView):
    def get(self, request):
        user = request.user
        rewards = ReferralReward.objects.filter(referrer=user).order_by('-created_at')

        paid = rewards.filter(status='paid')
        pending = rewards.filter(status='pending')

        return Response({
            'referral_code': user.referral_code,
            'total_referrals': rewards.count(),
            'paid_referrals': paid.count(),
            'pending_referrals': pending.count(),
            'total_points_earned': sum(r.points_awarded for r in paid),
            'total_naira_earned': str(sum(r.bonus_naira for r in paid)),
            'recent_referrals': ReferralRewardSerializer(rewards[:10], many=True).data,
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def validate_referral_code(request, code):
    """Check if a referral code is valid before registration."""
    exists = User.objects.filter(referral_code=code).exists()
    return Response({'valid': exists})


# ─── OAuth → JWT Bridge ───────────────────────────────
from django.contrib.auth import get_user_model as _get_user_model
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import RefreshToken as _RefreshToken


class OAuthTokenView(APIView):
    """
    Issue JWT tokens for a user authenticated via Django session (Google OAuth).
    Called by the oauth-success bridge page via JS fetch.
    Requires Django session auth (set by allauth after OAuth completes).
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        refresh = _RefreshToken.for_user(user)
        return Response({
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': UserProfileSerializer(user).data,
        })


# ─── Public Platform Stats ────────────────────────────────────
from django.contrib.auth import get_user_model as _get_user_model2


class PlatformStatsView(APIView):
    """Public stats for homepage — no auth required."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from apps.games.models import GameSession
        from apps.rewards.models import WithdrawalRequest
        from apps.quiz.models import Question, Category

        User = _get_user_model2()

        total_users      = User.objects.filter(is_active=True).count()
        total_games      = GameSession.objects.filter(status='completed').count()
        total_questions  = Question.objects.filter(is_active=True).count()
        total_categories = Category.objects.filter(is_active=True, parent=None).count()
        from django.db.models import Sum as _Sum
        total_withdrawn  = WithdrawalRequest.objects.filter(
            status='completed'
        ).aggregate(total=_Sum('amount_to_receive'))['total'] or 0

        return Response({
            'total_users':      total_users,
            'total_games':      total_games,
            'total_questions':  total_questions,
            'total_categories': total_categories,
            'total_withdrawn':  float(total_withdrawn),
        })
