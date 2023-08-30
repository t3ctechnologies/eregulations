from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from common.api import OpenApiQueryParameter
from resources.models import AbstractLocation
from resources.views.mixins import LocationExplorerViewSetMixin

from .functions import establish_client
from .models import Subject, UploadCategory, UploadedFile
from .serializers import SubjectSerializer, UploadCategorySerializer, UploadedFileSerializer


@extend_schema(
    description="Retrieve a list of Upload Categories",
)
class UploadCategoryViewset(viewsets.ViewSet):
    model = UploadCategory

    def list(self, request):
        queryset = self.model.objects.all()
        serializer = UploadCategorySerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    description="Retrieve a list of subjects.",
)
class SubjectViewset(viewsets.ViewSet):
    model = Subject

    def list(self, request):
        queryset = self.model.objects.all()
        serializer = SubjectSerializer(queryset, many=True)
        return Response(serializer.data)


class UploadedFileViewset(viewsets.ViewSet, LocationExplorerViewSetMixin):
    serializer_class = UploadedFileSerializer
    model = UploadedFile
    location_filter_prefix = "locations__"

    def get_queryset(self):
        locations = self.request.GET.getlist("locations")
        subjects = self.request.GET.getlist("subjects")
        categories = self.request.GET.getlist("categories")

        query = self.model.objects.all()

        q_obj = self.get_location_filter(locations)

        if q_obj:
            query = query.filter(q_obj)
        if subjects:
            query = query.filter(subject__id__in=subjects)
        if categories:
            query = query.filter(category__id__in=categories)

        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        categories_prefetch = UploadCategory.objects.all()
        subjects_prefetch = Subject.objects.all()

        query = query.prefetch_related(
            Prefetch("locations", queryset=locations_prefetch),
            Prefetch("subject", queryset=subjects_prefetch),
            Prefetch("category", queryset=categories_prefetch)).distinct()
        return query

    def get_serializer_context(self):
        context = {}
        context["location_details"] = self.request.GET.get("location_details", "true").lower() == "true"
        return context

    @extend_schema(
        description="Retrieve list of uploaded files",
        parameters=[
                    OpenApiQueryParameter("location_details",
                                          "Specify whether to show details of a location, or just the ID.",
                                          bool, False),
                    OpenApiQueryParameter("categories",
                                          "Limit results to only resources found within these categories. Use "
                                          "\"&categories=X&categories=Y\" for multiple.", int, False),
                    OpenApiQueryParameter("subjects",
                                          "Limit results to only resources found within these subjects. Use "
                                          "\"&subjects=X&subjects=Y\" for multiple.", int, False),
                    ] + LocationExplorerViewSetMixin.PARAMETERS
    )
    def list(self, request):
        queryset = self.get_queryset()
        context = self.get_serializer_context()
        serializer = UploadedFileSerializer(queryset, many=True, context=context)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("id")
        file = queryset.get(uid=id)
        serializer = UploadedFileSerializer(file, many=False)
        return Response(serializer.data)

    def generate_download_link(self, obj):
        s3_client = establish_client()
        try:
            return s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                            'Key': obj.file.name},
                                                    ExpiresIn=600)
        except Exception:
            print('Could not set up download url.')
            return 'Not available for download.'

    @extend_schema(description="Download a piece of internal resource")
    def download(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("id")
        file = queryset.get(uid=id)
        try:
            url = self.generate_download_link(file)
            response = HttpResponse(url, content_type='application/force-download')
            response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
            return response
        except Exception:
            print('Could not set up download url.')
            return 'Not available for download.'
