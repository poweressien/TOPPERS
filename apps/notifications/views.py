from rest_framework import generics, permissions, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'action_url', 'created_at']

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_read(request, pk):
    Notification.objects.filter(id=pk, user=request.user).update(is_read=True)
    return Response({'message': 'Marked as read.'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read.'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'unread_count': count})
