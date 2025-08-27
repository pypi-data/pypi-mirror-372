from django.db import models

import functools

from ichec_django_core.models import PortalMember, TimesStampMixin, content_file_name

from marinerg_facility.models import TestFacility


class AccessCall(TimesStampMixin):

    class Meta:
        verbose_name = "Access Call"
        verbose_name_plural = "Access Calls"

    class StatusChoice(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"
        DRAFT = "DRAFT", "Draft"

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=10, choices=StatusChoice.choices, default=StatusChoice.DRAFT
    )
    closing_date = models.DateTimeField()
    coordinator = models.ForeignKey(PortalMember, on_delete=models.CASCADE)

    board_chair = models.ForeignKey(
        PortalMember, on_delete=models.CASCADE, related_name="chaired_access_boards"
    )
    board_members = models.ManyToManyField(
        PortalMember,
        verbose_name="list of members",
        related_name="access_boards",
        blank=True,
    )

    applications_summary = models.FileField(
        null=True,
        upload_to=functools.partial(
            content_file_name, "access_call_applications_summary"
        ),
    )

    def __str__(self):
        return self.title

    @property
    def applications_summary_url(self):
        return "applications_summary" if self.applications_summary else ""


class AccessCallFacilityReview(TimesStampMixin):
    class Decision(models.TextChoices):
        ACCEPT = "ACCEPT", "Accept"
        REJECT = "REJECT", "Reject"

    decision = models.CharField(max_length=10, choices=Decision.choices)
    comments = models.TextField(blank=True)
    call = models.ForeignKey(AccessCall, on_delete=models.CASCADE)
    facility = models.ForeignKey(TestFacility, on_delete=models.CASCADE)
