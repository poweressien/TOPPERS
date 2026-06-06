from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from django.urls import path

User = get_user_model()


def _build_board(queryset, page=1, size=50):
    """Build a ranked leaderboard from a user queryset."""
    offset = (page - 1) * size
    users = queryset[offset: offset + size]
    result = []
    for rank_offset, user in enumerate(users, start=offset + 1):
        result.append({
            'rank': rank_offset,
            'user_id': str(user.id),
            'username': user.username,
            'avatar': user.avatar.url if user.avatar else None,
            'level': user.level,
            'level_name': user.level_name,
            'country': user.country,
        })
    return result


class GlobalLeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        qs = User.objects.filter(is_active=True).order_by('-total_points', '-total_games_played')
        board = _build_board(qs, page=page)

        # Add points for global board
        for i, row in enumerate(board):
            u = User.objects.get(id=row['user_id'])
            row['total_points'] = u.total_points
            row['total_games'] = u.total_games_played

        # Add requesting user's rank
        user_rank = None
        all_ids = list(User.objects.filter(is_active=True).order_by('-total_points').values_list('id', flat=True))
        if request.user.id in all_ids:
            user_rank = all_ids.index(request.user.id) + 1

        return Response({
            'leaderboard': board,
            'your_rank': user_rank,
            'your_points': request.user.total_points,
        })


class WeeklyLeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        from apps.games.models import GameSession
        from django.db.models import Sum, Count
        import datetime

        today = timezone.localdate()
        week_start = today - datetime.timedelta(days=today.weekday())

        scores = (
            GameSession.objects
            .filter(status='completed', start_time__date__gte=week_start)
            .values('user')
            .annotate(weekly_score=Sum('score'), games=Count('id'))
            .order_by('-weekly_score')[:50]
        )

        result = []
        for rank, row in enumerate(scores, start=1):
            try:
                u = User.objects.get(id=row['user'])
                result.append({
                    'rank': rank,
                    'username': u.username,
                    'avatar': u.avatar.url if u.avatar else None,
                    'weekly_score': row['weekly_score'],
                    'games_played': row['games'],
                    'country': u.country,
                })
            except User.DoesNotExist:
                pass

        return Response({'leaderboard': result, 'week_start': str(week_start)})


class MonthlyLeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        from apps.games.models import GameSession
        from django.db.models import Sum, Count

        today = timezone.localdate()
        month_start = today.replace(day=1)

        scores = (
            GameSession.objects
            .filter(status='completed', start_time__date__gte=month_start)
            .values('user')
            .annotate(monthly_score=Sum('score'), games=Count('id'))
            .order_by('-monthly_score')[:50]
        )

        result = []
        for rank, row in enumerate(scores, start=1):
            try:
                u = User.objects.get(id=row['user'])
                result.append({
                    'rank': rank,
                    'username': u.username,
                    'avatar': u.avatar.url if u.avatar else None,
                    'monthly_score': row['monthly_score'],
                    'games_played': row['games'],
                    'country': u.country,
                })
            except User.DoesNotExist:
                pass

        return Response({'leaderboard': result, 'month_start': str(month_start)})


# ─── URLs ─────────────────────────────────────────────────────
urlpatterns = [
    path('global/',  GlobalLeaderboardView.as_view(),  name='global_leaderboard'),
    path('weekly/',  WeeklyLeaderboardView.as_view(),  name='weekly_leaderboard'),
    path('monthly/', MonthlyLeaderboardView.as_view(), name='monthly_leaderboard'),
]
