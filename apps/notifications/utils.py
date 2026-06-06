def send_notification(user, title, message, notification_type='system', action_url='', extra_data=None):
    """Helper to create a notification for a user."""
    from .models import Notification
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
        extra_data=extra_data or {},
    )
