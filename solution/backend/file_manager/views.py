
from django.conf import settings
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.api import OpenApiQueryParameter
from common.constants import QUOTE_TYPES
from resources.models import AbstractLocation
from resources.views.mixins import LocationExplorerViewSetMixin, OptionalPaginationMixin

from .functions import establish_client, get_upload_link
from .models import DocumentType, Subject, UploadedFile
from .serializers import (
    AwsTokenSerializer,
    DocumentTypeSerializer,
    SubjectSerializer,
    UploadedFileSerializer,
)


@extend_schema(
    description="Retrieve a list of Upload Categories",
)
class UploadCategoryViewset(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    model = DocumentType

    def list(self, request):
        queryset = self.model.objects.all()
        serializer = DocumentTypeSerializer(queryset, many=True)
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


class UploadedFileViewset(viewsets.ReadOnlyModelViewSet, LocationExplorerViewSetMixin, OptionalPaginationMixin):
    permission_classes = (IsAuthenticated,)
    model = UploadedFile
    queryset = model.objects.all()
    location_filter_prefix = "locations__"
    pagination_class = OptionalPaginationMixin.pagination_class

    def make_headline(self, field, search_query, search_type):
        return SearchHeadline(
            field,
            SearchQuery(search_query, search_type=search_type, config="english"),
            start_sel='<span class="search-headline">',
            stop_sel='</span>',
            config="english",
            highlight_all=True,
        )

    def get_search_headlines(self, search_query, search_type):
        return {
            "document_name_headline": self.make_headline("document_name", search_query, search_type),
            "summary_headline": self.make_headline("summary", search_query, search_type),
        }

    def get_queryset(self):
        locations = self.request.GET.getlist("locations")
        subjects = self.request.GET.getlist("subjects")
        category = self.request.GET.getlist("category")
        search_query = self.request.GET.get("q")
        query = self.queryset

        q_obj = self.get_location_filter(locations)

        if q_obj:
            query = query.filter(q_obj)
        if subjects:
            query = query.filter(subjects__id__in=subjects)
        else:
            query = query.filter(subjects__isnull=False)
        if category:
            query = query.filter(category__id=category)

        locations_prefetch = AbstractLocation.objects.all().select_subclasses()
        doc_type_prefetch = DocumentType.objects.all()
        subjects_prefetch = Subject.objects.all()

        query = query.prefetch_related(
            Prefetch("locations", queryset=locations_prefetch),
            Prefetch("subjects", queryset=subjects_prefetch),
            Prefetch("document_type", queryset=doc_type_prefetch)).distinct()

        if search_query:
            (search_type, cover_density) = (
                ("phrase", True)
                if search_query.startswith(QUOTE_TYPES) and search_query.endswith(QUOTE_TYPES)
                else ("plain", False)
            )
            vector = SearchVector("document_name", weight="A", config="english") + \
                SearchVector("summary", weight="B", config="english") + \
                SearchVector("date", weight="C", config="english")
            query = query.annotate(
                rank=SearchRank(
                    vector,
                    SearchQuery(search_query, search_type=search_type, config="english"),
                    cover_density=cover_density,
                ),
                **self.get_search_headlines(search_query, search_type),
            )
            query = query.filter(Q(rank__gte=0.2) | Q(file_name__icontains=search_query))
        else:
            query = query.order_by('date', 'document_name')
        return query

    @extend_schema(
        description="Retrieve list of uploaded files",
        parameters=[
                    OpenApiQueryParameter("location_details",
                                          "Specify whether to show details of a location, or just the ID.",
                                          bool, False),
                    OpenApiQueryParameter("document_type",
                                          "Limit results to only resources found within this category. Use "
                                          "\"&document_type=X\"", int, False),
                    OpenApiQueryParameter("subjects",
                                          "Limit results to only resources found within these subjects. Use "
                                          "\"&subjects=X&subjects=Y\" for multiple.", int, False),
                    OpenApiQueryParameter("q",
                                          "Search for text within file metadata. Searches document_name, file name, "
                                          "date, and summary.", str, False),
                    ] + LocationExplorerViewSetMixin.PARAMETERS
    )
    def list(self, request):
        queryset = self.get_queryset()
        context = self.get_serializer_context()
        paginate = self.request.GET.get("paginate") != 'false'
        if paginate:
            queryset = self.paginate_queryset(queryset)
            serializer = UploadedFileSerializer(queryset, many=True, context=context)
            return self.get_paginated_response(serializer.data)
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
        key = obj.get_key()
        params = {'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                  'Key': key,
                  'ResponseContentDisposition': f"inline;filename={obj.file_name}"}
        if obj.extension() == '.pdf':
            params['ResponseContentType'] = "application/pdf"
        return s3_client.generate_presigned_url('get_object',
                                                Params=params,
                                                ExpiresIn=20)

    def upload(self, request, *args, **kwargs):
        id = kwargs.get("file_id")
        file_name = kwargs.get("file_name")
        uploaded_file = None
        if id:
            uploaded_file = UploadedFile.objects.get(uid=id)
            uploaded_file.file_name = file_name
        elif file_name:
            uploaded_file = UploadedFile(file_name=file_name)
            uploaded_file.save()
        else:
            raise Exception("File name not provided")

        if uploaded_file:
            result = get_upload_link(uploaded_file.get_key())
            serializer = AwsTokenSerializer(result)
            return Response(serializer.data)

    @extend_schema(description="Download a piece of internal resource")
    def download(self, request, *args, **kwargs):
        queryset = UploadedFile.objects.all()
        id = kwargs.get("file_id")
        file = queryset.get(uid=id)

        url = self.generate_download_link(file)
        response = HttpResponseRedirect(url)
        return response
