import random
from django.conf import settings
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.quiz.models import Question, Answer
from apps.rewards.services import PointsService, AchievementService
from .models import GameSession, GameAnswer, UserLifeline, DailyChallenge
from .serializers import (
    GameSessionSerializer, GameSessionDetailSerializer,
    SubmitAnswerSerializer, UseLifelineSerializer,
    GameAnswerSerializer, UserLifelineSerializer, GameSummarySerializer,
)

GAME_CONFIG = settings.GAME_CONFIG


def _pick_questions(mode, category=None):
    """Return ordered list of question UUIDs for a session."""
    qs = Question.objects.filter(is_active=True).prefetch_related('answers')
    if category:
        qs = qs.filter(category=category)

    def pick(diff, n):
        pool = list(qs.filter(difficulty=diff))
        return random.sample(pool, min(n, len(pool)))

    if mode == GameSession.MODE_CLASSIC:
        questions = pick('easy', 5) + pick('medium', 5) + pick('hard', 3) + pick('expert', 2)
    elif mode == GameSession.MODE_DAILY:
        questions = pick('easy', 3) + pick('medium', 4) + pick('hard', 3)
    elif mode == GameSession.MODE_SURVIVAL:
        # Start with easy, no predefined end
        questions = pick('easy', 10) + pick('medium', 10) + pick('hard', 10) + pick('expert', 5)
        random.shuffle(questions)
    elif mode == GameSession.MODE_SPEED:
        # Lots of easy/medium mixed
        questions = pick('easy', 15) + pick('medium', 15)
        random.shuffle(questions)
    else:
        questions = list(qs.order_by('?')[:10])

    return [str(q.id) for q in questions]


class GameSessionViewSet(ModelViewSet):
    """Core game session management."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameSessionSerializer

    def get_queryset(self):
        return GameSession.objects.filter(user=self.request.user).order_by('-start_time')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GameSessionDetailSerializer
        return GameSessionSerializer

    def create(self, request, *args, **kwargs):
        """Start a new game session."""
        user = request.user
        mode = request.data.get('mode', GameSession.MODE_CLASSIC)
        category_id = request.data.get('category')

        if mode not in dict(GameSession.MODE_CHOICES):
            return Response({'error': 'Invalid game mode.'}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce daily game limit
        user.reset_daily_games()
        if user.daily_games_played >= GAME_CONFIG['DAILY_GAME_LIMIT']:
            return Response({
                'error': 'Daily game limit reached.',
                'limit': GAME_CONFIG['DAILY_GAME_LIMIT'],
                'can_watch_ad': True,
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Daily mode — only one per day
        if mode == GameSession.MODE_DAILY:
            today = timezone.localdate()
            if DailyChallenge.objects.filter(user=user, date=today).exists():
                return Response({'error': 'You have already completed today\'s challenge.'}, status=status.HTTP_400_BAD_REQUEST)

        category = None
        if category_id:
            from apps.quiz.models import Category
            try:
                category = Category.objects.get(id=category_id)
            except Exception:
                return Response({'error': 'Invalid category.'}, status=status.HTTP_400_BAD_REQUEST)

        question_ids = _pick_questions(mode, category)
        if not question_ids:
            return Response({'error': 'Not enough questions available for this mode.'}, status=status.HTTP_400_BAD_REQUEST)

        session = GameSession.objects.create(
            user=user,
            mode=mode,
            category=category,
            question_ids=question_ids,
        )

        # Increment daily game count
        user.daily_games_played += 1
        user.save(update_fields=['daily_games_played'])

        return Response(GameSessionDetailSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='answer')
    def submit_answer(self, request, pk=None):
        """Submit an answer for the current question."""
        session = self.get_object()
        if session.status != GameSession.STATUS_ACTIVE:
            return Response({'error': 'Session is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_id = str(serializer.validated_data['question_id'])
        answer_id   = serializer.validated_data.get('answer_id')
        time_taken  = serializer.validated_data['time_taken']

        # Validate question belongs to this session
        if question_id not in session.question_ids:
            return Response({'error': 'Question not in this session.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.prefetch_related('answers').get(id=question_id)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check not already answered
        if GameAnswer.objects.filter(session=session, question=question).exists():
            return Response({'error': 'Already answered this question.'}, status=status.HTTP_400_BAD_REQUEST)

        # Evaluate answer
        chosen_answer = None
        is_correct = False
        if answer_id:
            try:
                chosen_answer = question.answers.get(id=answer_id)
                is_correct = chosen_answer.is_correct
            except Answer.DoesNotExist:
                return Response({'error': 'Answer not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Points calculation
        points = 0
        if is_correct:
            base_points = question.points_value
            points = int(base_points * session.multiplier)
            # Speed bonus: extra 20% if answered in < half the time limit
            if time_taken < (question.time_limit / 2):
                points = int(points * 1.2)

        # Survival mode: increase multiplier on correct streak
        if session.mode == GameSession.MODE_SURVIVAL and is_correct:
            session.multiplier = round(
                session.multiplier + GAME_CONFIG['SURVIVAL_MULTIPLIER_INCREMENT'], 2
            )

        # Record the answer
        GameAnswer.objects.create(
            session=session,
            question=question,
            chosen_answer=chosen_answer,
            is_correct=is_correct,
            time_taken_seconds=time_taken,
            points_earned=points,
        )

        # Update session totals
        session.score += points
        session.questions_answered += 1
        session.current_question_index += 1
        if is_correct:
            session.correct_answers += 1
        else:
            session.wrong_answers += 1
            # Survival mode ends on wrong answer
            if session.mode == GameSession.MODE_SURVIVAL:
                session.save()
                return self._finish_session(session)

        # Update question stats
        question.times_answered += 1
        if is_correct:
            question.times_correct += 1
        question.save(update_fields=['times_answered', 'times_correct'])

        # Check if session is complete
        is_complete = session.current_question_index >= len(session.question_ids)
        if is_complete:
            session.save()
            return self._finish_session(session)

        # Speed mode: check time limit exceeded
        if session.mode == GameSession.MODE_SPEED:
            elapsed = (timezone.now() - session.start_time).seconds
            if elapsed >= GAME_CONFIG['SPEED_MODE_DURATION']:
                session.save()
                return self._finish_session(session)

        session.save()

        # Return next question info
        next_idx = session.current_question_index
        next_question_id = session.question_ids[next_idx] if next_idx < len(session.question_ids) else None

        return Response({
            'is_correct': is_correct,
            'points_earned': points,
            'correct_answer': {
                'id': str(question.correct_answer.id) if question.correct_answer else None,
                'text': question.correct_answer.text if question.correct_answer else None,
            },
            'explanation': question.explanation,
            'session_score': session.score,
            'current_question_index': session.current_question_index,
            'next_question_id': next_question_id,
            'multiplier': session.multiplier,
            'session_complete': False,
        })

    def _finish_session(self, session):
        """Finalize session, award points, check achievements."""
        session.complete()
        user = session.user

        # Award points to user
        points_awarded = session.score
        PointsService.add_points(
            user=user,
            amount=points_awarded,
            transaction_type='earned_game',
            description=f'{session.get_mode_display()} – {session.correct_answers} correct',
            session=session,
        )

        # Update user stats
        user.total_games_played += 1
        user.total_correct_answers += session.correct_answers
        user.total_wrong_answers += session.wrong_answers
        user.save(update_fields=['total_games_played', 'total_correct_answers', 'total_wrong_answers'])

        # Track daily challenge
        if session.mode == GameSession.MODE_DAILY:
            today = timezone.localdate()
            DailyChallenge.objects.get_or_create(
                user=user, date=today,
                defaults={'session': session, 'streak_at_time': user.current_streak}
            )

        # Check achievements
        new_achievements = AchievementService.check_and_award(user)

        accuracy = 0.0
        if session.questions_answered > 0:
            accuracy = round((session.correct_answers / session.questions_answered) * 100, 1)

        summary = {
            'session_id': str(session.id),
            'mode': session.mode,
            'score': session.score,
            'correct_answers': session.correct_answers,
            'wrong_answers': session.wrong_answers,
            'total_questions': session.questions_answered,
            'accuracy': accuracy,
            'time_taken_seconds': session.time_taken_seconds or 0,
            'points_awarded': points_awarded,
            'new_total_points': user.total_points,
            'achievements_unlocked': [
                {'name': a.name, 'description': a.description} for a in new_achievements
            ],
            'session_complete': True,
        }
        return Response(summary)

    @action(detail=True, methods=['post'], url_path='use-lifeline')
    def use_lifeline(self, request, pk=None):
        """Use a lifeline for the current question."""
        session = self.get_object()
        if session.status != GameSession.STATUS_ACTIVE:
            return Response({'error': 'Session is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UseLifelineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lifeline_type = serializer.validated_data['lifeline_type']
        question_id   = serializer.validated_data['question_id']

        # Check lifeline not already used in this session
        if lifeline_type in session.lifelines_used:
            return Response({'error': f'{lifeline_type} already used in this session.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.prefetch_related('answers').get(id=question_id)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)

        result = {}

        if lifeline_type == 'fifty_fifty':
            correct = question.answers.filter(is_correct=True).first()
            wrong_answers = list(question.answers.filter(is_correct=False))
            keep_wrong = random.choice(wrong_answers) if wrong_answers else None
            eliminated = [
                str(a.id) for a in question.answers.all()
                if a.id != correct.id and (not keep_wrong or a.id != keep_wrong.id)
            ]
            result = {'eliminated_answer_ids': eliminated}

        elif lifeline_type == 'phone_friend':
            correct = question.answers.filter(is_correct=True).first()
            confidence = random.randint(75, 95)
            result = {
                'hint': f'My friend is {confidence}% confident the answer is: "{correct.text}"'
            }

        elif lifeline_type == 'ask_audience':
            correct = question.answers.filter(is_correct=True).first()
            all_answers = list(question.answers.all())
            audience = {}
            total = 100
            correct_pct = random.randint(45, 75)
            remaining = total - correct_pct
            for ans in all_answers:
                if str(ans.id) == str(correct.id):
                    audience[str(ans.id)] = correct_pct
                else:
                    # distribute remaining among wrong answers
                    split = remaining // max(1, len(all_answers) - 1)
                    audience[str(ans.id)] = split
            result = {'audience_votes': audience}

        elif lifeline_type == 'skip':
            # Move to next question without penalty
            session.current_question_index += 1
            session.save(update_fields=['current_question_index'])
            result = {'skipped': True, 'next_index': session.current_question_index}

        elif lifeline_type == 'second_chance':
            result = {'second_chance_granted': True}

        # Record lifeline usage
        session.lifelines_used.append(lifeline_type)
        session.save(update_fields=['lifelines_used'])

        return Response({'lifeline_type': lifeline_type, **result})

    @action(detail=True, methods=['post'], url_path='abandon')
    def abandon(self, request, pk=None):
        session = self.get_object()
        if session.status == GameSession.STATUS_ACTIVE:
            session.status = GameSession.STATUS_ABANDONED
            session.end_time = timezone.now()
            session.save()
        return Response({'message': 'Session abandoned.'})

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        sessions = self.get_queryset().filter(status=GameSession.STATUS_COMPLETED)[:20]
        return Response(GameSessionSerializer(sessions, many=True).data)


class LifelineView(APIView):
    """Get user's current lifeline inventory."""
    def get(self, request):
        lifelines = UserLifeline.objects.filter(user=request.user)
        return Response(UserLifelineSerializer(lifelines, many=True).data)


class DailyStatusView(APIView):
    """Check today's challenge and daily game status."""
    def get(self, request):
        user = request.user
        user.reset_daily_games()
        today = timezone.localdate()
        daily_done = DailyChallenge.objects.filter(user=user, date=today).exists()

        return Response({
            'daily_games_played': user.daily_games_played,
            'daily_game_limit': GAME_CONFIG['DAILY_GAME_LIMIT'],
            'games_remaining': max(0, GAME_CONFIG['DAILY_GAME_LIMIT'] - user.daily_games_played),
            'daily_challenge_completed': daily_done,
            'current_streak': user.current_streak,
        })
