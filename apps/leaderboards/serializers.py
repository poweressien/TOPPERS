from rest_framework import serializers
from .models import LeaderboardEntry

class LeaderboardEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = LeaderboardEntry
        fields = ['rank', 'user', 'username', 'avatar', 'period', 'points', 'games_played', 'challenges_won']

    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None
