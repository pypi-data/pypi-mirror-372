from rest_framework import serializers

from marinerg_test_access.models import AccessApplication


class AccessApplicationSerializer(serializers.HyperlinkedModelSerializer):

    call_title = serializers.CharField(
        source="call.title", required=False, read_only=True
    )
    applicant_username = serializers.CharField(
        source="applicant.username", required=False, read_only=True
    )

    class Meta:
        model = AccessApplication
        fields = [
            "url",
            "id",
            "device_details",
            "trl_stage",
            "objectives",
            "requirements",
            "facilities",
            "chosen_facility",
            "requires_testing",
            "requires_eng_support",
            "requires_prototyping",
            "requires_design",
            "requires_review",
            "request_start_date",
            "request_end_date",
            "dates_flexible",
            "confirmed_facility_discussion",
            "accepted_data_processing_terms",
            "safety_statement_url",
            "funding_statement_url",
            "summary_url",
            "applicant",
            "call",
            "created_at",
            "submitted",
            "updated_at",
            "status",
            "call_title",
            "applicant_username",
        ]
        read_only_fields = [
            "submitted",
            "applicant",
            "updated_at",
            "call_title",
            "safety_statement_url",
            "funding_statement_url",
            "summary_url",
            "applicant_username",
        ]
