from rest_framework import permissions, viewsets

from marinerg_test_access.models import AccessCall, AccessCallFacilityReview
from marinerg_test_access.serializers import (
    AccessCallSerializer,
    AccessCallFacilityReviewSerializer,
)


class AccessCallViewSet(viewsets.ModelViewSet):
    queryset = AccessCall.objects.all()
    serializer_class = AccessCallSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]


class AccessCallFacilityReviewViewSet(viewsets.ModelViewSet):
    queryset = AccessCallFacilityReview.objects.all()
    serializer_class = AccessCallFacilityReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
