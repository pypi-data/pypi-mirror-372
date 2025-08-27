from rest_framework import permissions, viewsets

from ichec_django_core.models import PortalMember
from ichec_django_core.view_sets import ObjectFileDownloadView, ObjectFileUploadView

from marinerg_test_access.models import AccessApplication
from marinerg_test_access.serializers import AccessApplicationSerializer


def is_consortium_admin(user):
    for group in user.groups.all():
        if group.name == "consortium_admins":
            return True
    return False


def is_on_access_board(application, user):
    if user.id == application.call.board_chair.id:
        return True

    for member in application.call.board_members.all():
        if member.id == user.id:
            return True
    return False


def is_call_coordinator(application, user):
    return application.call.coordinator.id == user.id


class ApplicationPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in ["OPTIONS", "HEAD", "POST"]:
            return True

        if obj.applicant.id == request.user.id:
            return True
        if is_consortium_admin(request.user):
            return True

        if request.method in ["GET", "PUT", "PATCH"]:
            if is_on_access_board(obj, request.user):
                return True
            if is_call_coordinator(obj, request.user):
                return True
        return False


class AccessApplicationViewSet(viewsets.ModelViewSet):
    queryset = AccessApplication.objects.all()
    serializer_class = AccessApplicationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        ApplicationPermissions,
    ]

    def get_queryset(self):
        queryset = AccessApplication.objects.all()
        applicant_id = self.request.query_params.get("user")
        if applicant_id is not None:
            queryset = queryset.filter(applicant__id=applicant_id)
        call_id = self.request.query_params.get("call")
        if call_id is not None:
            queryset = queryset.filter(call__id=call_id)
        facility_id = self.request.query_params.get("facility")
        if facility_id is not None:
            queryset = queryset.filter(facilities__id=facility_id)
        status = self.request.query_params.get("status")
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(applicant=PortalMember.objects.get(id=self.request.user.id))


class SafetyStatementDownloadView(ObjectFileDownloadView):
    model = AccessApplication
    file_field = "safety_statement"


class FundingStatementDownloadView(ObjectFileDownloadView):
    model = AccessApplication
    file_field = "funding_statement"


class SummaryDownloadView(ObjectFileDownloadView):
    model = AccessApplication
    file_field = "summary"


class SafetyStatementUploadView(ObjectFileUploadView):
    model = AccessApplication
    file_field = "safety_statement"


class FundingStatementUploadView(ObjectFileUploadView):
    model = AccessApplication
    file_field = "funding_statement"


class SummaryUploadView(ObjectFileUploadView):
    model = AccessApplication
    file_field = "summary"
