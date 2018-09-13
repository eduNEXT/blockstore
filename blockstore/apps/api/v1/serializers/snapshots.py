"""
Serializers for Snapshots.
"""

from django.core.files.storage import default_storage
from rest_framework import serializers

from ... import relations


class FileHyperlinkedIdentityField(relations.HyperlinkedIdentityField):
    """
    A HyperlinkedIdentityField for a nested FileInfo resource.
    """

    def get_url(self, obj, view_name, request, format):
        request = self.context['request']
        return self.reverse(
            self.context.get('detail_view_name', view_name),
            kwargs={
                'path': obj.path,
                **request.parser_context['kwargs'],
            },
            request=request,
            format=format,
        )


class FileDataField(serializers.FileField):
    """
    A FileField for FileInfo data field whose representation is a link to the file.
    """

    def get_attribute(self, obj):
        # We pass the object instance onto `to_representation`, not just the field attribute.
        return obj

    def to_representation(self, obj):
        request = self.context['request']
        data_location = "{}/data/{}".format(request.parser_context['kwargs']['bundle_uuid'], obj.hash_digest.hex())
        return self.context['request'].build_absolute_uri(default_storage.url(data_location))


class FileInfoSerializer(serializers.Serializer):
    """
    Serializer for a FileInfo object.
    """

    data = FileDataField()
    path = serializers.CharField()
    public = serializers.BooleanField()
    size = serializers.IntegerField(read_only=True)

    url = FileHyperlinkedIdentityField(
        lookup_field='path',
        lookup_url_kwarg='path',
        view_name='api:v1:bundlefile-detail',
    )