from django.urls import path

from . import views


app_name = "issues"


urlpatterns = [

    # ======================================================
    # CITIZEN
    # ======================================================

    path(
        "report/",
        views.report_issue,
        name="report_issue"
    ),

    path(
        "my-issues/",
        views.my_issues,
        name="my_issues"
    ),

    path(
        "map/",
        views.issue_map,
        name="issue_map"
    ),

    path(
        "nearby/",
        views.nearby_issues,
        name="nearby_issues"
    ),

    # ======================================================
    # GOVERNMENT
    # ======================================================

    path(
        "government/",
        views.government_issue_list,
        name="government_issue_list"
    ),

    path(
        "government/<int:issue_id>/",
        views.government_issue_detail,
        name="government_issue_detail"
    ),

    # ======================================================
    # ISSUE
    # ======================================================

    path(
        "<int:issue_id>/",
        views.issue_detail,
        name="issue_detail"
    ),

    path(
        "<int:issue_id>/upvote/",
        views.toggle_upvote,
        name="toggle_upvote"
    ),


    path(
    "api/gemini/analyze/",
    views.gemini_analyze_issue,
    name="gemini_analyze_issue"
    ),

]