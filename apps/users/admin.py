from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # ==========================================================
    # USER LIST PAGE
    # ==========================================================

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "government_request_status",
        "is_verified",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "role",
        "government_request_status",
        "is_verified",
        "is_active",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )

    ordering = ("-date_joined",)


    # ==========================================================
    # GOVERNMENT REQUEST ACTIONS
    # ==========================================================

    actions = [
        "approve_government_requests",
        "reject_government_requests",
    ]


    @admin.action(description="Approve selected government requests")
    def approve_government_requests(self, request, queryset):

        pending_users = queryset.filter(
            government_request_status=User.GovernmentRequestStatus.PENDING
        )

        updated = pending_users.update(
            role=User.Role.GOVERNMENT,
            government_request_status=User.GovernmentRequestStatus.APPROVED,
            is_verified=True,
        )

        self.message_user(
            request,
            f"{updated} government request(s) approved successfully."
        )


    @admin.action(description="Reject selected government requests")
    def reject_government_requests(self, request, queryset):

        pending_users = queryset.filter(
            government_request_status=User.GovernmentRequestStatus.PENDING
        )

        updated = pending_users.update(
            role=User.Role.CITIZEN,
            government_request_status=User.GovernmentRequestStatus.REJECTED,
            is_verified=False,
        )

        self.message_user(
            request,
            f"{updated} government request(s) rejected."
        )


    # ==========================================================
    # EDIT USER PAGE
    # ==========================================================

    fieldsets = (

        (
            "Login Information",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),

        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "profile_image",
                )
            },
        ),

        (
            "JanMitra Information",
            {
                "fields": (
                    "role",
                    "government_request_status",
                    "is_verified",
                    "preferred_language",
                )
            },
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        # IMPORTANT:
        # Do NOT put date_joined or updated_at here.
        # Both fields are non-editable because they use
        # auto_now_add=True / auto_now=True in the model.
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                )
            },
        ),
    )


    # ==========================================================
    # ADD USER PAGE
    # ==========================================================

    add_fieldsets = (
        (
            "Create User",
            {
                "classes": ("wide",),

                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "role",
                    "government_request_status",
                    "is_verified",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )