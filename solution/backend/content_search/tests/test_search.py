import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from content_search.functions import add_to_index
from content_search.models import ContentIndex
from file_manager.models import Subject, UploadedFile
from resources.models import FederalRegisterDocument, Section, SupplementalContent


class SearchTest(TestCase):
    def check_exclusive_response(self, response, id):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["doc_name_string"], self.internal_docs[id]["document_name"])

    def login(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_user', password='test')  # noqa: S106
        self.client.force_authenticate(self.user)

    def clean_up(self):
        SupplementalContent.objects.all().delete()
        FederalRegisterDocument.objects.all().delete()
        UploadedFile.objects.all().delete()
        ContentIndex.objects.all().delete()

    def setUp(self):
        self.clean_up()
        self.internal_docs = []
        self.location1 = Section.objects.create(title="42", part="433", section_id="1")
        self.location2 = Section.objects.create(title="33", part="31", section_id="22")

        self.subject1 = Subject.objects.create()
        self.subject2 = Subject.objects.create()

        with open("content_search/tests/fixtures/sample_supplemental.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = SupplementalContent.objects.create(**data)
                if i == 0:  # only assign location and subject on item 0
                    file.locations.set([self.location2])
                    file.subjects.set([self.subject2])
                    file.save()

        with open("content_search/tests/fixtures/sample_fr_doc.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                file = FederalRegisterDocument.objects.create(**data)
                if i == 0:  # only assign location and subject on item 0
                    file.locations.set([self.location2])
                    file.subjects.set([self.subject2])
                    file.save()

        with open("content_search/tests/fixtures/sample_files.json", "r") as f:
            for i, data in enumerate(json.load(f)):
                self.internal_docs.append(data)
                file = UploadedFile.objects.create(**data)
                if i == 0:  # only assign location and subject on item 0
                    file.locations.set([self.location2])
                    file.subjects.set([self.subject2])
                    file.save()

        for x in SupplementalContent.objects.all():
            add_to_index(x)
        for x in FederalRegisterDocument.objects.all():
            add_to_index(x)
        for x in UploadedFile.objects.all():
            add_to_index(x)

    def test_no_query_not_logged_in(self):
        response = self.client.get("/v3/content-search/?resource-type=external")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)
        response = self.client.get("/v3/content-search/?resource-type=internal")
        self.assertEqual(len(response.data), 6)
        response = self.client.get("/v3/content-search/?resource-type=all")
        self.assertEqual(len(response.data), 6)

    def test_no_query_logged_in(self):
        self.login()
        response = self.client.get("/v3/content-search/?resource-type=external")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)
        response = self.client.get("/v3/content-search/?resource-type=internal")
        self.assertEqual(len(response.data), 3)
        response = self.client.get("/v3/content-search/?resource-type=all")
        self.assertEqual(len(response.data), 9)

    def test_single_response_queries(self):
        self.login()
        response = self.client.get("/v3/content-search/?q=fire&resource-type=external")
        self.assertEqual(len(response.data), 1)
        response = self.client.get("/v3/content-search/?q=fire&resource-type=all")
        self.assertEqual(len(response.data), 2)

    def test_multi_response_query(self):
        # This tests to ensure files are correctly *included* based on search terms
        self.login()
        response = self.client.get("/v3/file-manager/files?q=file")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["document_name"], self.internal_docs[0]["document_name"])
        self.assertEqual(response.data[1]["document_name"], self.internal_docs[2]["document_name"])
        response = self.client.get("/v3/content-search/?q=fire&resource-type=external")
        self.assertEqual(len(response.data), 1)
        response = self.client.get("/v3/content-search/?q=fire&resource-type=all")
        self.assertEqual(len(response.data), 2)

    def test_search_by_filename_variations(self):
        self.login()
        words = ["cheese", "pokemon"]
        for word in words:
            response = self.client.get(f"/v3/content-search/?resource-type=internal&q={word}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn(word, response.data[0]["file_name_string"])

    def test_inclusive_location_filter(self):
        self.login()
        response = self.client.get("/v3/content-search/?resource-type=internal&q=test&locations=42.433")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        response = self.client.get("/v3/content-search/?resource-type=internal&q=test&locations=42.433&locations=33.31")
        self.check_exclusive_response(response, 0)

    def test_inclusive_subject_filter(self):
        self.login()
        response = self.client.get(f"/v3/content-search/?resource-type=internal&q=test&subjects={self.subject1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        response = self.client.get(
            f"/v3/content-search/?resource-type=internal&q=test&subjects={self.subject1.id}&subjects={self.subject2.id}")
        self.check_exclusive_response(response, 0)
