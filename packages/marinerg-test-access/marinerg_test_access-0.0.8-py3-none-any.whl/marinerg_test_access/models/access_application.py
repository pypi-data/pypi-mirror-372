from django.db import models
from django.conf import settings
from django.utils import timezone

import zipfile
import os
import functools
from pathlib import Path
from weasyprint import HTML

from ichec_django_core.models import PortalMember, TimesStampMixin, content_file_name

from marinerg_facility.models import TestFacility

from .access_call import AccessCall


def generate_summary(
    instance,
    output_field: str = "summary",
    include_fields=("funding_statement", "safety_statement"),
):

    html = f"<html><body><p>Device Details:{instance.device_details}</p></body></html>"
    pdf_bytes = HTML(string=html).write_pdf()

    field_path = f"{instance._meta.model_name}_{output_field}"
    work_dir = Path(settings.MEDIA_ROOT) / field_path
    os.makedirs(work_dir, exist_ok=True)

    filename = f"{field_path}_{instance.id}.zip"
    with zipfile.ZipFile(
        work_dir / filename, "w", zipfile.ZIP_DEFLATED, False
    ) as zip_file:
        for field in include_fields:
            if instance.getattr(field):
                zip_file.write(
                    Path(settings.MEDIA_ROOT) / instance.getattr(field).name,
                    arcname=f"{field}.pdf",
                )
        zip_file.writestr("summary.pdf", pdf_bytes)

    instance.summary.name = os.path.join(field_path, filename)
    instance.save()


class AccessApplication(TimesStampMixin):

    class Meta:
        verbose_name = "Access Application"
        verbose_name_plural = "Access Application"

    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        SUBMITTED = "SUBMITTED", "Submitted"
        AWAITING_FACILITY_REVIEW = "FACILITY", "Awaiting Facility Review"
        AWAITING_BOARD_REVIEW = "BOARD", "Awaiting Board Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    facilities = models.ManyToManyField(
        TestFacility, related_name="application_choices", blank=True
    )

    chosen_facility = models.ForeignKey(
        TestFacility, on_delete=models.CASCADE, related_name="applications", null=True
    )

    device_details = models.TextField(blank=True)
    trl_stage = models.IntegerField(default=0, blank=True)
    objectives = models.TextField(blank=True)
    requirements = models.TextField(blank=True)

    requires_testing = models.BooleanField(default=False)
    requires_eng_support = models.BooleanField(default=False)
    requires_prototyping = models.BooleanField(default=False)
    requires_design = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)

    request_start_date = models.DateTimeField(null=True)
    request_end_date = models.DateTimeField(null=True)
    dates_flexible = models.BooleanField(default=False)

    confirmed_facility_discussion = models.BooleanField(default=False)
    accepted_data_processing_terms = models.BooleanField(default=False)

    applicant = models.ForeignKey(PortalMember, on_delete=models.CASCADE)
    call = models.ForeignKey(AccessCall, on_delete=models.CASCADE)

    safety_statement = models.FileField(
        null=True,
        upload_to=functools.partial(
            content_file_name, "access_application_safety_statement"
        ),
    )
    funding_statement = models.FileField(
        null=True,
        upload_to=functools.partial(
            content_file_name, "access_application_funding_statement"
        ),
    )
    summary = models.FileField(null=True)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.CREATED
    )

    submitted = models.DateTimeField(null=True)
    __last_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__last_status = str(self.status)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):

        if (
            str(self.status).lower() == "submitted"
            and self.__last_status.lower() == "created"
        ):
            self.submitted = timezone.now()
            generate_summary(self)
            self.status = "FACILITY"
        self.__last_status = str(self.status)

        super().save(force_insert, force_update, *args, **kwargs)

    def __str__(self):
        return f"{self.applicant.email} application for '{self.call.title}'"

    @property
    def safety_statement_url(self):
        return "safety_statement" if self.safety_statement else ""

    @property
    def funding_statement_url(self):
        return "funding_statement" if self.funding_statement else ""

    @property
    def summary_url(self):
        return "summary" if self.summary else ""
