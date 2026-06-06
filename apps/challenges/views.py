import random
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, permissions, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers

from apps.quiz.models import Question
from apps.rewards.services import PointsService
from apps.rewards.models import PointTransaction
from .models import LiveChallenge, ChallengeResult

User = get_user_model()


# ─── Serializers ──────────────────────────────────────────────

class ChallengeSerializer(serializers.ModelSerializer):
    challenger_username = serializers.CharField(source='challenger.username', read_only=True)
    challenged_username = serializers.CharField(source='challenged.username', read_only=True)
    winner_username = serializers.CharField(source='winner.username', read_only=True)

    class Meta:
        model = LiveChallenge
        fields = [
            'id', 'challenger', 'challenger_username',
            'challenged', 'challenged_username',
            'category', 'status', 'winner', 'winner_username',
            'bonus_points', 'created_at', 'expires_at', 'completed_at',
        ]
        read_only_fields = ['id', 'challenger', 'status', 'winner', 'created_at', 'expires_at']


class SendChallengeSerializer(serializers.Serializer):
    challenged_username = serializers.CharField()
    category_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_challenged_username(self, value):
        try:
            return User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f'User "{value}" not found.')


class ChallengeResultSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ChallengeResult
        fields = ['user', 'username', 'score', 'correct_answers', 'wrong_answers', 'time_taken_seconds', 'completed']


# ─── Views ────────────────────────────────────────────────────

class ChallengeViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChallengeSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        return LiveChallenge.objects.filter(
            Q(challenger=user) | Q(challenged=user)
        ).select_related('challenger', 'challenged', 'winner').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Send a challenge to another user."""
        s = SendChallengeSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        challenged_user = s.validated_data['challenged_username']
        category_id = s.validated_data.get('category_id')

        if challenged_user == request.user:
            return Response({'error': 'You cannot challenge yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # Pick 10 questions
        qs = Question.objects.filter(is_active=True)
        if category_id:
            qs = qs.filter(category_id=category_id)
        questions = random.sample(list(qs), min(10, qs.count()))
        question_ids = [str(q.id) for q in questions]

        challenge = LiveChallenge.objects.create(
            challenger=request.user,
            challenged=challenged_user,
            category_id=category_id,
            question_ids=question_ids,
        )

        # Notify the challenged user
        try:
            from apps.notifications.utils import send_notification
            send_notification(
                user=challenged_user,
                title=f'{request.user.username} challenged you!',
                message=f'You have 24 hours to accept.',
                notification_type='challenge',
            )
        except Exception:
            pass

        return Response(ChallengeSerializer(challenge).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        challenge = self.get_object()
        if challenge.challenged != request.user:
            return Response({'error': 'Not your challenge.'}, status=status.HTTP_403_FORBIDDEN)
        if challenge.status != LiveChallenge.STATUS_PENDING:
            return Response({'error': 'Challenge is no longer pending.'}, status=status.HTTP_400_BAD_REQUEST)
        if challenge.is_expired():
            challenge.status = LiveChallenge.STATUS_EXPIRED
            challenge.save()
            return Response({'error': 'Challenge has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        challenge.status = LiveChallenge.STATUS_ACCEPTED
        challenge.save()

        # Create result slots for both players
        ChallengeResult.objects.get_or_create(challenge=challenge, user=challenge.challenger)
        ChallengeResult.objects.get_or_create(challenge=challenge, user=challenge.challenged)

        return Response({'message': 'Challenge accepted!', 'challenge': ChallengeSerializer(challenge).data})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        challenge = self.get_object()
        if challenge.challenged != request.user:
            return Response({'error': 'Not your challenge.'}, status=status.HTTP_403_FORBIDDEN)
        challenge.status = LiveChallenge.STATUS_DECLINED
        challenge.save()
        return Response({'message': 'Challenge declined.'})

    @action(detail=True, methods=['post'], url_path='submit-score')
    def submit_score(self, request, pk=None):
        """Submit final score after completing the challenge questions."""
        challenge = self.get_object()
        if challenge.status not in [LiveChallenge.STATUS_ACCEPTED, LiveChallenge.STATUS_IN_PROGRESS]:
            return Response({'error': 'Challenge not active.'}, status=status.HTTP_400_BAD_REQUEST)

        score = request.data.get('score', 0)
        correct = request.data.get('correct_answers', 0)
        wrong = request.data.get('wrong_answers', 0)
        time_taken = request.data.get('time_taken_seconds', 0)

        result, _ = ChallengeResult.objects.get_or_create(challenge=challenge, user=request.user)
        result.score = score
        result.correct_answers = correct
        result.wrong_answers = wrong
        result.time_taken_seconds = time_taken
        result.completed = True
        result.completed_at = timezone.now()
        result.save()

        challenge.status = LiveChallenge.STATUS_IN_PROGRESS
        challenge.save()

        # Check if both players have submitted
        results = ChallengeResult.objects.filter(challenge=challenge)
        if results.count() == 2 and all(r.completed for r in results):
            self._resolve_challenge(challenge, results)

        return Response({'message': 'Score submitted.', 'your_score': score})

    def _resolve_challenge(self, challenge, results):
        r_list = list(results)
        r1, r2 = r_list[0], r_list[1]

        # Winner = higher score; tie-break = faster time
        if r1.score > r2.score:
            winner_result = r1
        elif r2.score > r1.score:
            winner_result = r2
        else:
            winner_result = r1 if r1.time_taken_seconds <= r2.time_taken_seconds else r2

        challenge.winner = winner_result.user
        challenge.status = LiveChallenge.STATUS_COMPLETED
        challenge.completed_at = timezone.now()
        challenge.save()

        # Award bonus points to winner
        PointsService.add_points(
            user=winner_result.user,
            amount=challenge.bonus_points,
            transaction_type=PointTransaction.TYPE_CHALLENGE_WIN,
            description=f'Challenge win vs {challenge.challenger.username if winner_result.user == challenge.challenged else challenge.challenged.username}',
        )

        # Update win stat
        winner_result.user.total_challenges_won += 1
        winner_result.user.save(update_fields=['total_challenges_won'])

        # Notify both players
        loser = r2.user if winner_result == r1 else r1.user
        try:
            from apps.notifications.utils import send_notification
            send_notification(
                winner_result.user,
                'You won the challenge! 🎉',
                f'+{challenge.bonus_points} bonus points awarded.',
                'challenge',
            )
            send_notification(
                loser,
                'Challenge over',
                f'{winner_result.user.username} won this round. Better luck next time!',
                'challenge',
            )
        except Exception:
            pass

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        challenge = self.get_object()
        results = ChallengeResult.objects.filter(challenge=challenge)
        return Response({
            'challenge': ChallengeSerializer(challenge).data,
            'results': ChallengeResultSerializer(results, many=True).data,
        })

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Challenges waiting for the user's response."""
        qs = LiveChallenge.objects.filter(
            challenged=request.user, status=LiveChallenge.STATUS_PENDING
        )
        return Response(ChallengeSerializer(qs, many=True).data)


# ─── URLs ─────────────────────────────────────────────────────

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', ChallengeViewSet, basename='challenge')

urlpatterns = [path('', include(router.urls))]
