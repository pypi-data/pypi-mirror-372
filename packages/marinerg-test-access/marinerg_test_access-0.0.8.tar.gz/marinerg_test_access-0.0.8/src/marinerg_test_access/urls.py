from django.urls import path

from .view_sets import (
    AccessApplicationViewSet,
    FundingStatementDownloadView,
    SafetyStatementDownloadView,
    SummaryDownloadView,
    FundingStatementUploadView,
    SafetyStatementUploadView,
    SummaryUploadView,
    AccessCallViewSet,
    AccessCallFacilityReviewViewSet,
    AccessApplicationFacilityReviewViewSet,
    AccessApplicationBoardReviewViewSet,
    FacilityTestReportViewSet,
)


def register_drf_views(router):
    router.register(r"access_calls", AccessCallViewSet)
    router.register(r"access_call_facility_reviews", AccessCallFacilityReviewViewSet)
    router.register(r"access_applications", AccessApplicationViewSet)
    router.register(
        r"access_application_facility_reviews", AccessApplicationFacilityReviewViewSet
    )
    router.register(
        r"access_application_board_reviews", AccessApplicationBoardReviewViewSet
    )
    router.register(r"facility_test_reports", FacilityTestReportViewSet)


urlpatterns = [
    path(
        r"access_applications/<int:pk>/safety_statement",
        SafetyStatementDownloadView.as_view(),
        name="safety_statements",
    ),
    path(
        r"access_applications/<int:pk>/funding_statement",
        FundingStatementDownloadView.as_view(),
        name="funding_statements",
    ),
    path(
        r"access_applications/<int:pk>/summary",
        SummaryDownloadView.as_view(),
        name="summaries",
    ),
    path(
        r"access_applications/<int:pk>/safety_statement/upload",
        SafetyStatementUploadView.as_view(),
        name="safety_statements_upload",
    ),
    path(
        r"access_applications/<int:pk>/funding_statement/upload",
        FundingStatementUploadView.as_view(),
        name="funding_statement_upload",
    ),
    path(
        r"access_applications/<int:pk>/summary/upload",
        SummaryUploadView.as_view(),
        name="summaries_upload",
    ),
]
