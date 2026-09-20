from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .models import Notification


@login_required
def notification_list(request):

    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related("issue")

    unread_count = notifications.filter(
        is_read=False
    ).count()

    context = {
        "notifications": notifications,
        "unread_count": unread_count,
    }

    return render(
        request,
        "notifications/notification_list.html",
        context
    )


@login_required
def mark_notification_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True

    notification.save(
        update_fields=["is_read"]
    )

    if notification.issue:

        return redirect(
            "issues:issue_detail",
            issue_id=notification.issue.id
        )

    return redirect(
        "notifications:list"
    )


@login_required
def mark_all_notifications_read(request):

    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    messages.success(
        request,
        _("All notifications have been marked as read.")
    )

    return redirect(
        "notifications:list"
    )