from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Issue(models.Model):

    CATEGORY_CHOICES = [
        ("road", _("Road & Potholes")),
        ("streetlight", _("Street Lights")),
        ("garbage", _("Garbage & Sanitation")),
        ("water", _("Water Supply")),
        ("drainage", _("Drainage")),
        ("electricity", _("Electricity")),
        ("traffic", _("Traffic")),
        ("other", _("Other")),
    ]

    STATUS_CHOICES = [
        ("reported", _("Reported")),
        ("under_review", _("Under Review")),
        ("in_progress", _("In Progress")),
        ("resolved", _("Resolved")),
        ("rejected", _("Rejected")),
    ]

    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="issues"
    )

    upvoted_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="upvoted_issues",
        blank=True
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    image = models.ImageField(
        upload_to="issues/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="reported"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


# ==========================================================
# GOVERNMENT PROOF IMAGE
# ==========================================================

class IssueProofImage(models.Model):

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="proof_images"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_issue_proofs"
    )

    image = models.ImageField(
        upload_to="issue_proofs/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Proof for Issue #{self.issue.id}"


# ==========================================================
# ISSUE STATUS HISTORY
# ==========================================================

class IssueStatusHistory(models.Model):

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    old_status = models.CharField(
        max_length=30
    )

    new_status = models.CharField(
        max_length=30
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issue_status_changes"
    )

    note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"Issue #{self.issue.id}: "
            f"{self.old_status} → {self.new_status}"
        )