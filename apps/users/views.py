from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.issues.models import Issue


from django.db.models import Count
from django.db.models.functions import TruncMonth


from .forms import CitizenRegistrationForm, CitizenProfileForm
from .models import User


# =============================================================
# REGISTRATION
# =============================================================

def register(request):

    if request.user.is_authenticated:
        return redirect("users:dashboard")

    if request.method == "POST":

        form = CitizenRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # -------------------------------------------------
            # SECURITY:
            # Every newly registered account starts as CITIZEN.
            # A user can never directly register as GOVERNMENT.
            # -------------------------------------------------

            user.role = User.Role.CITIZEN

            user.is_verified = False
            user.is_active = True

            # -------------------------------------------------
            # GOVERNMENT ACCESS REQUEST
            # -------------------------------------------------

            if form.cleaned_data.get(
                "request_government_role"
            ):

                user.government_request_status = (
                    User.GovernmentRequestStatus.PENDING
                )

            else:

                user.government_request_status = (
                    User.GovernmentRequestStatus.NONE
                )

            # -------------------------------------------------
            # PASSWORD
            # -------------------------------------------------

            user.set_password(
                form.cleaned_data["password1"]
            )

            user.save()

            # -------------------------------------------------
            # SUCCESS MESSAGE
            # -------------------------------------------------

            if form.cleaned_data.get(
                "request_government_role"
            ):

                messages.success(
                    request,
                    "Your account has been created. "
                    "Your government access request is pending "
                    "administrator approval."
                )

            else:

                messages.success(
                    request,
                    "Your JanMitra account has been created successfully."
                )

            return redirect("users:login")

    else:

        form = CitizenRegistrationForm()

    return render(
        request,
        "users/register.html",
        {
            "form": form
        }
    )


# =============================================================
# LOGIN
# =============================================================

def user_login(request):

    if request.user.is_authenticated:
        return redirect("users:dashboard")

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is not None:

            login(request, user)

            return redirect("users:dashboard")

        messages.error(
            request,
            "Invalid email or password."
        )

    return render(
        request,
        "users/login.html",
    )


# =============================================================
# DASHBOARD
# =============================================================

@login_required
def dashboard(request):

    # ---------------------------------------------------------
    # GOVERNMENT DASHBOARD
    # ---------------------------------------------------------

    if request.user.is_government:

        total_issues = Issue.objects.count()

        reported_issues = Issue.objects.filter(
            status="reported"
        ).count()

        under_review_issues = Issue.objects.filter(
            status="under_review"
        ).count()

        in_progress_issues = Issue.objects.filter(
            status="in_progress"
        ).count()

        resolved_issues = Issue.objects.filter(
            status="resolved"
        ).count()

        rejected_issues = Issue.objects.filter(
            status="rejected"
        ).count()

        pending_issues = (
            under_review_issues
            + in_progress_issues
        )

        context = {
            "total_issues": total_issues,
            "reported_issues": reported_issues,
            "under_review_issues": under_review_issues,
            "in_progress_issues": in_progress_issues,
            "pending_issues": pending_issues,
            "resolved_issues": resolved_issues,
            "rejected_issues": rejected_issues,
        }

        return render(
            request,
            "users/government_dashboard.html",
            context,
        )

    # ---------------------------------------------------------
    # CITIZEN DASHBOARD
    # ---------------------------------------------------------

    return render(
        request,
        "users/citizen_dashboard.html",
    )




# ---------------------------------------------------------
# GOVERNMENT ANALYTICS
# ---------------------------------------------------------


@login_required
def government_analytics(request):

    # ==========================================================
    # GOVERNMENT ACCESS
    # ==========================================================

    if not request.user.is_government:
        messages.error(
            request,
            "You do not have permission to access government analytics."
        )

        return redirect("users:dashboard")


    # ==========================================================
    # BASIC COUNTS
    # ==========================================================

    total_issues = Issue.objects.count()

    reported_issues = Issue.objects.filter(
        status="reported"
    ).count()

    under_review_issues = Issue.objects.filter(
        status="under_review"
    ).count()

    in_progress_issues = Issue.objects.filter(
        status="in_progress"
    ).count()

    resolved_issues = Issue.objects.filter(
        status="resolved"
    ).count()

    rejected_issues = Issue.objects.filter(
        status="rejected"
    ).count()


    # ==========================================================
    # PENDING ISSUES
    # ==========================================================

    pending_issues = (
        under_review_issues
        + in_progress_issues
    )


    # ==========================================================
    # RESOLUTION RATE
    # ==========================================================

    if total_issues > 0:
        resolution_rate = round(
            (resolved_issues / total_issues) * 100,
            1
        )
    else:
        resolution_rate = 0


    # ==========================================================
    # STATUS DISTRIBUTION
    # ==========================================================

    status_data = Issue.objects.values(
        "status"
    ).annotate(
        count=Count("id")
    ).order_by("status")


    status_labels = []
    status_counts = []

    status_names = dict(
        Issue.STATUS_CHOICES
    )


    for item in status_data:

        status_labels.append(
            status_names.get(
                item["status"],
                item["status"]
            )
        )

        status_counts.append(
            item["count"]
        )


    # ==========================================================
    # CATEGORY DISTRIBUTION
    # ==========================================================

    category_data = Issue.objects.values(
        "category"
    ).annotate(
        count=Count("id")
    ).order_by("-count")


    category_labels = []
    category_counts = []

    category_names = dict(
        Issue.CATEGORY_CHOICES
    )


    for item in category_data:

        category_labels.append(
            category_names.get(
                item["category"],
                item["category"]
            )
        )

        category_counts.append(
            item["count"]
        )


    # ==========================================================
    # MONTHLY ISSUE TREND
    # ==========================================================

    monthly_data = (
        Issue.objects
        .annotate(
            month=TruncMonth("created_at")
        )
        .values("month")
        .annotate(
            count=Count("id")
        )
        .order_by("month")
    )


    monthly_labels = []
    monthly_counts = []


    for item in monthly_data:

        if item["month"]:

            monthly_labels.append(
                item["month"].strftime("%b %Y")
            )

            monthly_counts.append(
                item["count"]
            )


    # ==========================================================
    # MOST REPORTED CATEGORY
    # ==========================================================

    most_reported_category = None

    if category_data:

        first_category = category_data[0]

        most_reported_category = category_names.get(
            first_category["category"],
            first_category["category"]
        )


    # ==========================================================
    # CONTEXT
    # ==========================================================

    context = {

        "total_issues": total_issues,

        "reported_issues": reported_issues,

        "under_review_issues": under_review_issues,

        "in_progress_issues": in_progress_issues,

        "pending_issues": pending_issues,

        "resolved_issues": resolved_issues,

        "rejected_issues": rejected_issues,

        "resolution_rate": resolution_rate,

        "most_reported_category": most_reported_category,

        "status_labels": status_labels,

        "status_counts": status_counts,

        "category_labels": category_labels,

        "category_counts": category_counts,

        "monthly_labels": monthly_labels,

        "monthly_counts": monthly_counts,
    }


    return render(
        request,
        "users/government_analytics.html",
        context
    )



# =============================================================
# PROFILE
# =============================================================

@login_required
def profile(request):

    # Government users currently don't use the citizen profile.
    if request.user.is_government:
        return redirect("users:dashboard")

    if request.method == "POST":

        form = CitizenProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect(
                "users:profile"
            )

    else:

        form = CitizenProfileForm(
            instance=request.user
        )

    return render(
        request,
        "users/profile.html",
        {
            "form": form,
            "profile_user": request.user,
        }
    )


# =============================================================
# LOGOUT
# =============================================================

@login_required
def user_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "users:login"
    )