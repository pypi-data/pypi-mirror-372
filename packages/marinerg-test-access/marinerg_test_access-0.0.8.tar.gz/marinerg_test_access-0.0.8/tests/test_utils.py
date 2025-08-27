from ichec_django_core.models import PortalMember

from ichec_django_core.utils.test_utils import add_group_permissions

from marinerg_test_access.models import AccessCall, AccessApplication


def setup_access_call():
    coordinator = PortalMember.objects.get(username="access_call_coordinator")
    access_call_board_member = PortalMember.objects.get(
        username="access_call_board_member"
    )

    access_call = AccessCall.objects.create(
        title="Test access call",
        description="Description of access call",
        status="OPEN",
        closing_date="2024-11-11",
        coordinator=coordinator,
        board_chair=access_call_board_member,
    )

    access_call.board_members.set([access_call_board_member])

    add_group_permissions(
        "consortium_admins", AccessCall, ["change_accesscall", "add_accesscall"]
    )
    return access_call


def setup_application(call, applicant="test_applicant"):
    applicant = PortalMember.objects.get(username=applicant)
    AccessApplication.objects.create(applicant=applicant, call=call)
