from rest_framework import serializers

from marinerg_test_access.models import AccessCall, AccessCallFacilityReview


class AccessCallSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessCall
        fields = [
            "title",
            "description",
            "status",
            "closing_date",
            "coordinator",
            "created_at",
            "updated_at",
            "id",
            "url",
            "board_chair",
            "board_members",
            "applications_summary",
        ]
        read_only_fields = ["created_at", "updated_at", "applications_summary"]


class AccessCallFacilityReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessCallFacilityReview
        fields = ["decision", "comments", "call", "facility"]
