from .models import Notification


def create_notification(
    recipient,
    notification_type,
    title,
    message,
    issue=None,
):
    """
    Create a notification for a user.
    """

    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        issue=issue,
    )