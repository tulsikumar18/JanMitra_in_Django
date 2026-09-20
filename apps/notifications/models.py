from django.conf import settings

from django.db import models

from django.utils.translation import gettext_lazy as _


class Notification(models.Model):

    class NotificationType(models.TextChoices):

        ISSUE_SUBMITTED = (
            "issue_submitted",
            _("Issue Submitted"),
        )

        UNDER_REVIEW = (
            "under_review",
            _("Under Review"),
        )

        IN_PROGRESS = (
            "in_progress",
            _("In Progress"),
        )

        RESOLVED = (
            "resolved",
            _("Resolved"),
        )

        REJECTED = (
            "rejected",
            _("Rejected"),
        )

        REWARD = (
            "reward",
            _("Reward"),
        )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    issue = models.ForeignKey(
        "issues.Issue",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    # ==========================================================
    # LOCALIZED NOTIFICATION TITLE
    # ==========================================================

    def get_localized_title(self):

        titles = {

            self.NotificationType.ISSUE_SUBMITTED:
                _("Issue Submitted"),

            self.NotificationType.UNDER_REVIEW:
                _("Issue Under Review"),

            self.NotificationType.IN_PROGRESS:
                _("Issue In Progress"),

            self.NotificationType.RESOLVED:
                _("Issue Resolved"),

            self.NotificationType.REJECTED:
                _("Issue Rejected"),

            self.NotificationType.REWARD:
                _("Reward"),
        }

        return titles.get(
            self.notification_type,
            self.title,
        )

    # ==========================================================
    # LOCALIZED NOTIFICATION MESSAGE
    # ==========================================================

    def get_localized_message(self):

        # ------------------------------------------------------
        # If notification has no related issue,
        # keep the original stored message.
        # ------------------------------------------------------

        if not self.issue:
            return self.message

        issue_title = self.issue.title

        messages = {

            # --------------------------------------------------
            # ISSUE SUBMITTED
            # --------------------------------------------------

            self.NotificationType.ISSUE_SUBMITTED:
                _(
                    'Your issue "%(title)s" has been '
                    'reported successfully.'
                ) % {
                    "title": issue_title
                },

            # --------------------------------------------------
            # UNDER REVIEW
            # --------------------------------------------------

            self.NotificationType.UNDER_REVIEW:
                _(
                    'Your reported issue "%(title)s" '
                    'is now under review.'
                ) % {
                    "title": issue_title
                },

            # --------------------------------------------------
            # IN PROGRESS
            # --------------------------------------------------

            self.NotificationType.IN_PROGRESS:
                _(
                    'Work has started on your reported '
                    'issue "%(title)s".'
                ) % {
                    "title": issue_title
                },

            # --------------------------------------------------
            # RESOLVED
            # --------------------------------------------------

            self.NotificationType.RESOLVED:
                _(
                    'Your reported issue "%(title)s" '
                    'has been successfully resolved.'
                ) % {
                    "title": issue_title
                },

            # --------------------------------------------------
            # REJECTED
            # --------------------------------------------------

            self.NotificationType.REJECTED:
                _(
                    'Your reported issue "%(title)s" '
                    'has been rejected.'
                ) % {
                    "title": issue_title
                },
        }

        return messages.get(
            self.notification_type,
            self.message,
        )

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):

        return f"{self.recipient.email} - {self.title}"