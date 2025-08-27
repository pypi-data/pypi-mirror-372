from rest_framework import serializers

from marinerg_test_access.models import (
    FacilityTestReport,
    AccessApplicationFacilityReview,
    AccessApplicationBoardReview,
)


class FacilityTestReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FacilityTestReport
        fields = [
            "creator",
            "report",
            "dataset_uri",
            "confirmed_complies_data_mgmt",
            "application",
        ]


class AccessApplicationFacilityReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessApplicationFacilityReview
        fields = [
            "confirmed_preapplication_discussion",
            "confirmed_app_info_in_line_with_discussion",
            "supporting_comments",
            "supporting_documents",
            "application",
            "facility",
        ]


class AccessApplicationBoardReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessApplicationBoardReview
        fields = ["decision", "comments", "call", "creator"]
