from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        CITIZEN = "citizen", "Citizen"
        GOVERNMENT = "government", "Government"

    class GovernmentRequestStatus(models.TextChoices):
        NONE = "none", "No Request"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    # =========================================================
    # BASIC INFORMATION
    # =========================================================

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    # =========================================================
    # USER ROLE
    # =========================================================

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CITIZEN
    )

    # =========================================================
    # GOVERNMENT ACCESS REQUEST
    # =========================================================

    government_request_status = models.CharField(
        max_length=20,
        choices=GovernmentRequestStatus.choices,
        default=GovernmentRequestStatus.NONE
    )

    # =========================================================
    # PROFILE
    # =========================================================

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    # =========================================================
    # ACCOUNT STATUS
    # =========================================================

    is_verified = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =========================================================
    # LANGUAGE
    # =========================================================

    preferred_language = models.CharField(
        max_length=2,
        choices=[
            ("en", "English"),
            ("kn", "Kannada"),
            ("hi", "Hindi"),
        ],
        default="en"
    )

    # =========================================================
    # USER MANAGER
    # =========================================================

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "first_name"
    ]

    # =========================================================
    # STRING REPRESENTATION
    # =========================================================

    def __str__(self):
        return self.email


    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


    def get_short_name(self):
        return self.first_name

    # =========================================================
    # ROLE HELPERS
    # =========================================================

    @property
    def is_citizen(self):
        return self.role == self.Role.CITIZEN

    @property
    def is_government(self):
        return self.role == self.Role.GOVERNMENT