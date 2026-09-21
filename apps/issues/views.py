from apps import issues

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import IssueForm
from .models import Issue, IssueProofImage, IssueStatusHistory

from apps.rewards.models import CoinWallet, CoinTransaction

from apps.notifications.services import create_notification
from apps.notifications.models import Notification

from math import radians, sin, cos, sqrt, atan2

import json

from .gemini_service import analyze_civic_issue


# ==========================================================
# CITIZEN - REPORT ISSUE
# ==========================================================

@login_required
def report_issue(request):

    if request.method == "POST":

        form = IssueForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            issue = form.save(commit=False)

            issue.citizen = request.user

            issue.save()

            messages.success(
                request,
                _(
                    "Your issue has been reported successfully. "
                    "Issue #%(issue_id)s is now being tracked."
                ) % {
                    "issue_id": issue.id
                }
            )

            return redirect("issues:my_issues")

    else:

        form = IssueForm()

    return render(
        request,
        "issues/report_issue.html",
        {
            "form": form
        }
    )


# ==========================================================
# CITIZEN - MY ISSUES
# ==========================================================

@login_required
def my_issues(request):

    issues = request.user.issues.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "issues/my_issues.html",
        {
            "issues": issues
        }
    )



# ==========================================================
# CITIZEN - DELETE ISSUE
# ==========================================================

@login_required
@require_POST
def delete_issue(request, issue_id):

    # Only allow the citizen who created the issue
    # to delete that issue.
    issue = get_object_or_404(
        Issue.objects.filter(
            citizen=request.user
        ),
        id=issue_id
    )

    issue_title = issue.title

    # ------------------------------------------------------
    # Collect uploaded files before deleting database rows
    # ------------------------------------------------------

    files_to_delete = []

    if issue.image:
        files_to_delete.append(
            issue.image
        )

    proof_images = list(
        issue.proof_images.all()
    )

    for proof in proof_images:

        if proof.image:

            files_to_delete.append(
                proof.image
            )

    try:

        # --------------------------------------------------
        # DATABASE DELETION
        # --------------------------------------------------

        with transaction.atomic():

            # Delete notifications belonging to this issue.
            Notification.objects.filter(
                issue=issue
            ).delete()

            # Issue.delete() will cascade to:
            #
            # - IssueProofImage
            # - IssueStatusHistory
            # - upvoted_by relationship rows
            #
            # because these relationships are connected
            # to Issue with CASCADE / M2M behavior.

            issue.delete()

        # --------------------------------------------------
        # DELETE ACTUAL MEDIA FILES
        # --------------------------------------------------
        #
        # This is important for Cloudinary.
        #
        # FieldFile.delete() calls the configured Django
        # storage backend, so the Cloudinary asset is removed
        # instead of only removing the database reference.

        for uploaded_file in files_to_delete:

            try:

                uploaded_file.delete(
                    save=False
                )

            except Exception as storage_error:

                print(
                    "JanMitra: unable to delete issue media:",
                    storage_error
                )

        # --------------------------------------------------
        # SUCCESS MESSAGE
        # --------------------------------------------------

        messages.success(
            request,
            _(
                'Issue "%(title)s" was deleted successfully.'
            ) % {
                "title": issue_title
            }
        )

    except Exception as error:

        print(
            "JanMitra: issue deletion failed:",
            error
        )

        messages.error(
            request,
            _(
                "Unable to delete this issue right now. "
                "Please try again."
            )
        )

    return redirect(
        "issues:my_issues"
    )


# ==========================================================
# CITIZEN - ISSUE MAP
# ==========================================================

@login_required
def issue_map(request):

    # Bengaluru approximate geographic boundaries

    BENGALURU_MIN_LAT = 12.80
    BENGALURU_MAX_LAT = 13.20
    BENGALURU_MIN_LON = 77.40
    BENGALURU_MAX_LON = 77.80

    issues = Issue.objects.filter(
        latitude__gte=BENGALURU_MIN_LAT,
        latitude__lte=BENGALURU_MAX_LAT,
        longitude__gte=BENGALURU_MIN_LON,
        longitude__lte=BENGALURU_MAX_LON,
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "issues/issue_map.html",
        {
            "issues": issues,
            "category_choices": Issue.CATEGORY_CHOICES,
        }
    )


# ==========================================================
# ISSUE DETAIL
# ==========================================================

@login_required
def issue_detail(request, issue_id):

    issue = get_object_or_404(
        Issue.objects.select_related("citizen"),
        id=issue_id
    )

    proof_images = issue.proof_images.select_related(
        "uploaded_by"
    ).all()

    status_history = issue.status_history.select_related(
        "changed_by"
    ).all()

    return render(
        request,
        "issues/issue_detail.html",
        {
            "issue": issue,
            "proof_images": proof_images,
            "status_history": status_history,
        }
    )


# ==========================================================
# CITIZEN - TOGGLE UPVOTE
# ==========================================================

@login_required
def toggle_upvote(request, issue_id):

    issue = get_object_or_404(
        Issue,
        id=issue_id
    )

    # Only POST requests are allowed

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "error": _("Invalid request method.")
            },
            status=405
        )


    # A citizen cannot support their own issue

    if issue.citizen == request.user:

        return JsonResponse(
            {
                "success": False,
                "error": _("You cannot upvote your own issue."),
                "can_upvote": False
            },
            status=403
        )


    # Toggle upvote

    if issue.upvoted_by.filter(
        id=request.user.id
    ).exists():

        issue.upvoted_by.remove(
            request.user
        )

        has_upvoted = False

    else:

        issue.upvoted_by.add(
            request.user
        )

        has_upvoted = True


    return JsonResponse(
        {
            "success": True,
            "issue_id": issue.id,
            "has_upvoted": has_upvoted,
            "upvotes": issue.upvoted_by.count(),
            "can_upvote": True
        }
    )


# ==========================================================
# CITIZEN - NEARBY ISSUES
# ==========================================================

@login_required
def nearby_issues(request):

    try:

        latitude = float(
            request.GET.get("latitude")
        )

        longitude = float(
            request.GET.get("longitude")
        )

    except (TypeError, ValueError):

        return JsonResponse(
            {
                "success": False,
                "error": _("Invalid latitude or longitude.")
            },
            status=400
        )


    # Search radius in kilometres

    SEARCH_RADIUS_KM = 0.5


    # Bengaluru bounding box

    BENGALURU_MIN_LAT = 12.80
    BENGALURU_MAX_LAT = 13.15

    BENGALURU_MIN_LNG = 77.40
    BENGALURU_MAX_LNG = 77.80


    # Reject locations outside Bengaluru

    if not (
        BENGALURU_MIN_LAT <= latitude <= BENGALURU_MAX_LAT
        and
        BENGALURU_MIN_LNG <= longitude <= BENGALURU_MAX_LNG
    ):

        return JsonResponse(
            {
                "success": True,
                "count": 0,
                "issues": []
            }
        )


    # Approximate bounding box

    lat_delta = SEARCH_RADIUS_KM / 111

    lng_delta = SEARCH_RADIUS_KM / (
        111 * cos(radians(latitude))
    )


    candidates = Issue.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,

        latitude__gte=latitude - lat_delta,
        latitude__lte=latitude + lat_delta,

        longitude__gte=longitude - lng_delta,
        longitude__lte=longitude + lng_delta,

    ).exclude(
        status="rejected"
    )


    nearby = []


    for issue in candidates:

        issue_lat = float(issue.latitude)

        issue_lng = float(issue.longitude)


        # Haversine formula

        earth_radius_km = 6371

        lat1 = radians(latitude)

        lat2 = radians(issue_lat)


        delta_lat = radians(
            issue_lat - latitude
        )

        delta_lng = radians(
            issue_lng - longitude
        )


        a = (
            sin(delta_lat / 2) ** 2
            +
            cos(lat1)
            * cos(lat2)
            * sin(delta_lng / 2) ** 2
        )


        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )


        distance_km = earth_radius_km * c


        if distance_km <= SEARCH_RADIUS_KM:

            nearby.append(
                {
                    "id": issue.id,

                    "title": issue.title,

                    "description": issue.description,

                    "category": issue.category,

                    "category_name":
                        issue.get_category_display(),

                    "status": issue.status,

                    "status_name":
                        issue.get_status_display(),

                    "location": issue.location,

                    "latitude": issue.latitude,

                    "longitude": issue.longitude,

                    "upvotes":
                        issue.upvoted_by.count(),

                    "has_upvoted":
                        issue.upvoted_by.filter(
                            id=request.user.id
                        ).exists(),

                    "can_upvote":
                        issue.citizen_id != request.user.id,

                    "distance_meters":
                        round(
                            distance_km * 1000
                        ),

                    "created_at":
                        issue.created_at.strftime(
                            "%d %b %Y"
                        ),
                }
            )


    # Closest issue first

    nearby.sort(
        key=lambda issue:
            issue["distance_meters"]
    )


    return JsonResponse(
        {
            "success": True,
            "count": len(nearby),
            "issues": nearby
        }
    )


# ==========================================================
# GOVERNMENT - ISSUE MANAGEMENT
# ==========================================================


@login_required
def government_issue_list(request):

    # ------------------------------------------------------
    # Only approved government officials can access this page
    # ------------------------------------------------------

    if not request.user.is_government:

        messages.error(
            request,
            _(
                "You do not have permission to access "
                "government issue management."
            )
        )

        return redirect(
            "users:dashboard"
        )


    # ------------------------------------------------------
    # Start with all issues
    # ------------------------------------------------------

    issues = Issue.objects.select_related(
        "citizen"
    ).order_by(
        "-created_at"
    )


    # ------------------------------------------------------
    # Search
    # ------------------------------------------------------

    search_query = request.GET.get(
        "search",
        ""
    ).strip()


    if search_query:

        issues = issues.filter(

            Q(title__icontains=search_query)

            |

            Q(description__icontains=search_query)

            |

            Q(location__icontains=search_query)

            |

            Q(citizen__email__icontains=search_query)

            |

            Q(citizen__first_name__icontains=search_query)

            |

            Q(citizen__last_name__icontains=search_query)

        )


    # ------------------------------------------------------
    # Category filter
    # ------------------------------------------------------

    selected_category = request.GET.get(
        "category",
        ""
    )


    if selected_category:

        issues = issues.filter(
            category=selected_category
        )


    # ------------------------------------------------------
    # Status filter
    # ------------------------------------------------------

    selected_status = request.GET.get(
        "status",
        ""
    )


    if selected_status == "pending":

        issues = issues.filter(
            status__in=[
                "under_review",
                "in_progress"
            ]
        )

    elif selected_status:

        issues = issues.filter(
            status=selected_status
        )


    # ------------------------------------------------------
    # Context
    # ------------------------------------------------------

    context = {

        "issues": issues,

        "search_query":
            search_query,

        "selected_category":
            selected_category,

        "selected_status":
            selected_status,

        "category_choices":
            Issue.CATEGORY_CHOICES,

        "status_choices":
            Issue.STATUS_CHOICES,

        "total_issues":
            issues.count(),

    }


    return render(
        request,
        "issues/government_issue_list.html",
        context
    )


# ==========================================================
# GOVERNMENT - ISSUE DETAIL
# ==========================================================


STATUS_TRANSITIONS = {

    "reported": [
        "under_review",
        "rejected",
    ],

    "under_review": [
        "in_progress",
        "rejected",
    ],

    "in_progress": [
        "under_review",
        "resolved",
    ],

    "resolved": [],

    "rejected": [],

}


@login_required
def government_issue_detail(request, issue_id):

    # ==========================================================
    # GOVERNMENT ACCESS
    # ==========================================================

    if not request.user.is_government:

        messages.error(
            request,
            _(
                "You do not have permission to access "
                "government issue management."
            )
        )

        return redirect(
            "users:dashboard"
        )


    # ==========================================================
    # GET ISSUE
    # ==========================================================

    issue = get_object_or_404(
        Issue.objects.select_related("citizen"),
        id=issue_id
    )


    # ==========================================================
    # HANDLE POST REQUEST
    # ==========================================================

    if request.method == "POST":


        # ======================================================
        # STATUS UPDATE
        # ======================================================

        if "update_status" in request.POST:

            new_status = request.POST.get(
                "status"
            )


            note = request.POST.get(
                "status_note",
                ""
            ).strip()


            current_status = issue.status


            # --------------------------------------------------
            # Check whether status exists
            # --------------------------------------------------

            valid_statuses = dict(
                Issue.STATUS_CHOICES
            )


            if new_status not in valid_statuses:

                messages.error(
                    request,
                    _("Invalid issue status.")
                )

                return redirect(
                    "issues:government_issue_detail",
                    issue_id=issue.id
                )


            # --------------------------------------------------
            # Check workflow transition
            # --------------------------------------------------

            allowed_statuses = STATUS_TRANSITIONS.get(
                current_status,
                []
            )


            if new_status not in allowed_statuses:

                messages.error(
                    request,
                    _(
                        "An issue cannot move directly from "
                        "'%(current_status)s' to "
                        "'%(new_status)s'."
                    ) % {
                        "current_status":
                            issue.get_status_display(),

                        "new_status":
                            dict(
                                Issue.STATUS_CHOICES
                            ).get(
                                new_status
                            ),
                    }
                )

                return redirect(
                    "issues:government_issue_detail",
                    issue_id=issue.id
                )


            # --------------------------------------------------
            # RESOLVED REQUIRES PROOF
            # --------------------------------------------------

            if new_status == "resolved":

                proof_exists = (
                    IssueProofImage.objects
                    .filter(issue=issue)
                    .exists()
                )


                if not proof_exists:

                    messages.error(
                        request,
                        _(
                            "Please upload at least one "
                            "resolution proof image before "
                            "marking this issue as resolved."
                        )
                    )

                    return redirect(
                        "issues:government_issue_detail",
                        issue_id=issue.id
                    )


            # --------------------------------------------------
            # Save history
            # --------------------------------------------------

            with transaction.atomic():

                IssueStatusHistory.objects.create(

                    issue=issue,

                    old_status=current_status,

                    new_status=new_status,

                    changed_by=request.user,

                    note=note

                )


                issue.status = new_status

                issue.save()


                # --------------------------------------------------
                # Create notification for the citizen
                # --------------------------------------------------

                status_notification_data = {

                    "under_review": (

                        Notification.NotificationType.UNDER_REVIEW,

                        _("Issue Under Review"),

                        _(
                            'Your reported issue '
                            '"%(title)s" is now under review.'
                        ) % {
                            "title": issue.title
                        }

                    ),

                    "in_progress": (

                        Notification.NotificationType.IN_PROGRESS,

                        _("Issue In Progress"),

                        _(
                            'Work has started on your reported issue '
                            '"%(title)s".'
                        ) % {
                            "title": issue.title
                        }

                    ),

                    "resolved": (

                        Notification.NotificationType.RESOLVED,

                        _("Issue Resolved"),

                        _(
                            'Your reported issue '
                            '"%(title)s" has been successfully resolved.'
                        ) % {
                            "title": issue.title
                        }

                    ),

                    "rejected": (

                        Notification.NotificationType.REJECTED,

                        _("Issue Rejected"),

                        _(
                            'Your reported issue '
                            '"%(title)s" has been rejected.'
                        ) % {
                            "title": issue.title
                        }

                    ),

                }


                if new_status in status_notification_data:

                    (
                        notification_type,
                        title,
                        message
                    ) = status_notification_data[
                        new_status
                    ]


                    create_notification(

                        recipient=issue.citizen,

                        notification_type=
                            notification_type,

                        title=title,

                        message=message,

                        issue=issue,

                    )


                # --------------------------------------------------
                # Award coins only when the issue is resolved
                # --------------------------------------------------

                if new_status == "resolved":

                    COINS_FOR_RESOLUTION = 50


                    wallet, created = (
                        CoinWallet.objects.get_or_create(
                            citizen=issue.citizen
                        )
                    )


                    reward_exists = (
                        CoinTransaction.objects
                        .filter(
                            wallet=wallet,
                            issue=issue,
                            transaction_type=
                                CoinTransaction
                                .TransactionType
                                .EARNED
                        )
                        .exists()
                    )


                    if not reward_exists:

                        wallet.balance += (
                            COINS_FOR_RESOLUTION
                        )

                        wallet.total_earned += (
                            COINS_FOR_RESOLUTION
                        )


                        wallet.save(
                            update_fields=[
                                "balance",
                                "total_earned",
                                "updated_at"
                            ]
                        )


                        CoinTransaction.objects.create(

                            wallet=wallet,

                            transaction_type=
                                CoinTransaction
                                .TransactionType
                                .EARNED,

                            coins=
                                COINS_FOR_RESOLUTION,

                            issue=issue,

                            description=_(
                                "Issue #%(issue_id)s "
                                "successfully resolved"
                            ) % {
                                "issue_id": issue.id
                            }

                        )

                else:

                    messages.success(
                        request,
                        _(
                            "Issue #%(issue_id)s moved to "
                            "%(status)s."
                        ) % {
                            "issue_id": issue.id,
                            "status":
                                issue.get_status_display()
                        }
                    )


            return redirect(
                "issues:government_issue_detail",
                issue_id=issue.id
            )


        # ======================================================
        # GOVERNMENT PROOF UPLOAD
        # ======================================================

        if "upload_proof" in request.POST:

            files = request.FILES.getlist(
                "images"
            )


            if not files:

                messages.error(
                    request,
                    _("Please select at least one proof image.")
                )

                return redirect(
                    "issues:government_issue_detail",
                    issue_id=issue.id
                )


            uploaded_count = 0


            for image in files:

                if not image.content_type.startswith(
                    "image/"
                ):

                    continue


                IssueProofImage.objects.create(

                    issue=issue,

                    uploaded_by=request.user,

                    image=image

                )


                uploaded_count += 1


            if uploaded_count > 0:

                messages.success(
                    request,
                    _(
                        "%(count)s proof image(s) "
                        "uploaded successfully."
                    ) % {
                        "count": uploaded_count
                    }
                )

            else:

                messages.error(
                    request,
                    _("No valid image files were uploaded.")
                )


            return redirect(
                "issues:government_issue_detail",
                issue_id=issue.id
            )


    # ==========================================================
    # GET STATUS HISTORY
    # ==========================================================

    status_history = issue.status_history.select_related(
        "changed_by"
    ).all()


    # ==========================================================
    # AVAILABLE NEXT STATUSES
    # ==========================================================

    next_statuses = STATUS_TRANSITIONS.get(
        issue.status,
        []
    )


    next_status_choices = [

        (value, label)

        for value, label in Issue.STATUS_CHOICES

        if value in next_statuses

    ]


    # ==========================================================
    # PROOF IMAGES
    # ==========================================================

    proof_images = issue.proof_images.select_related(
        "uploaded_by"
    ).all()


    # ==========================================================
    # CONTEXT
    # ==========================================================

    context = {

        "issue": issue,

        "status_history":
            status_history,

        "status_choices":
            next_status_choices,

        "proof_images":
            proof_images,

        "current_status":
            issue.status,

    }


    return render(
        request,
        "issues/government_issue_detail.html",
        context
    )


# ==========================================================
# AI ASSISTANT - GEMINI
# ==========================================================

@require_POST
def gemini_analyze_issue(request):
    """
    Analyze a civic issue using Gemini.
    """

    try:

        data = json.loads(
            request.body
        )


        problem = data.get(
            "problem",
            ""
        ).strip()


        if len(problem) < 5:

            return JsonResponse(
                {
                    "success": False,
                    "error": _(
                        "Please provide a more detailed problem."
                    )
                },
                status=400
            )


        result = analyze_civic_issue(
            problem
        )


        return JsonResponse(
            {
                "success": True,
                "result": result
            }
        )


    except Exception as error:

        print(
            "Gemini analysis error:",
            error
        )


        return JsonResponse(
            {
                "success": False,
                "error": _(
                    "Unable to analyze the issue right now."
                )
            },
            status=500
        )