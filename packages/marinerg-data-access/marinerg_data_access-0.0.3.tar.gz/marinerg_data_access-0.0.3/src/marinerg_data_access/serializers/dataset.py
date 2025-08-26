from rest_framework import serializers

from marinerg_data_access.models import Dataset


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            "creator",
            "title",
            "description",
            "uri",
            "is_public",
            "access_instructions",
        ]
