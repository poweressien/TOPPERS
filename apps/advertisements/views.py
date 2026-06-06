from django.utils import timezone
from rest_framework import generics, permissions, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as http_status
from .models import Advertisement, AdView

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'ad_type', 'media_url', 'duration_seconds', 'reward_type', 'reward_value']

class ActiveAdsView(generics.ListAPIView):
    serializer_class = AdSerializer
    def get_queryset(self):
        return Advertisement.objects.filter(is_active=True)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def record_ad_view(request, pk):
    try:
        ad = Advertisement.objects.get(id=pk, is_active=True)
    except Advertisement.DoesNotExist:
        return Response({'error': 'Ad not found.'}, status=http_status.HTTP_404_NOT_FOUND)

    user = request.user
    today = timezone.localdate()
    views_today = AdView.objects.filter(user=user, advertisement=ad, viewed_at__date=today).count()
    if views_today >= ad.max_views_per_user_per_day:
        return Response({'error': 'Daily ad view limit reached for this ad.'}, status=http_status.HTTP_429_TOO_MANY_REQUESTS)

    ad_view = AdView.objects.create(user=user, advertisement=ad)
    ad.total_views += 1
    ad.save(update_fields=['total_views'])

    reward_msg = ''
    if ad.reward_type == 'extra_game':
        user.daily_games_played = max(0, user.daily_games_played - ad.reward_value)
        user.save(update_fields=['daily_games_played'])
        reward_msg = f'+{ad.reward_value} extra game session(s) unlocked.'
    elif ad.reward_type == 'bonus_points':
        from apps.rewards.services import PointsService
        from apps.rewards.models import PointTransaction
        PointsService.add_points(user, ad.reward_value, PointTransaction.TYPE_AD_BONUS, 'Ad watch reward')
        reward_msg = f'+{ad.reward_value} bonus points awarded.'
    elif ad.reward_type == 'lifeline':
        from apps.games.models import UserLifeline
        ul, _ = UserLifeline.objects.get_or_create(user=user, lifeline_type='skip')
        ul.quantity += ad.reward_value
        ul.save()
        reward_msg = f'+{ad.reward_value} skip lifeline(s) added.'

    ad_view.reward_granted = True
    ad_view.save(update_fields=['reward_granted'])

    return Response({'message': 'Ad viewed successfully.', 'reward': reward_msg})
