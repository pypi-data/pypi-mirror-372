from rest_framework import viewsets, permissions

from marinerg_data_access.models import Dataset
from marinerg_data_access.serializers import DatasetSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
