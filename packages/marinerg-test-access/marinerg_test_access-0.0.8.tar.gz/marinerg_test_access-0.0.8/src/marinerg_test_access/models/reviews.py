from django.db import models

from ichec_django_core.models import PortalMember, TimesStampMixin

from marinerg_facility.models import TestFacility

from .access_call import AccessCall
from .access_application import AccessApplication


class FacilityTestReport(TimesStampMixin):

    creator = models.ForeignKey(PortalMember, on_delete=models.CASCADE)
    report = models.FileField(null=True)
    dataset_uri = models.CharField(max_length=200, blank=True)
    confirmed_complies_data_mgmt = models.BooleanField(default=False)
    application = models.ForeignKey(AccessApplication, on_delete=models.CASCADE)


class AccessApplicationFacilityReview(TimesStampMixin):

    confirmed_preapplication_discussion = models.BooleanField(default=False)
    confirmed_app_info_in_line_with_discussion = models.BooleanField(default=False)
    supporting_comments = models.TextField(blank=True)
    supporting_documents = models.FileField(null=True)
    facility = models.ForeignKey(TestFacility, on_delete=models.CASCADE)
    application = models.ForeignKey(AccessApplication, on_delete=models.CASCADE)


class AccessApplicationBoardReview(TimesStampMixin):
    class Decision(models.TextChoices):
        ACCEPT = "1", "ACCEPT"
        REJECT = "2", "REJECT"

    decision = models.CharField(max_length=10, choices=Decision.choices)
    comments = models.TextField(blank=True)
    call = models.ForeignKey(AccessCall, on_delete=models.CASCADE)
    creator = models.ForeignKey(PortalMember, on_delete=models.CASCADE)
