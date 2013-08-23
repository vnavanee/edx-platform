"""
Basic test for views in search
"""

from collections import namedtuple
from BaseHTTPServer import BaseHTTPRequestHandler

from django.test import TestCase
from django.test.utils import override_settings
import requests

import search.views as views
from search.models import SearchResults
from mocks import StubServer, StubRequestHandler

class PersonalServer(StubServer):

    def log_request(self, request_type, path, content):
        self.requests.append(self.request(request_type, path, content))
        if path.endswith("_search"):
            self.content = "{}"


class ViewTest(TestCase):
    """
    Basic test class for base view case. A small test, but one that adresses some blind spots
    """

    def setUp(self):
        self.stub = PersonalServer(StubRequestHandler)

    def test_stub_server(self):
        check = requests.get("http://127.0.0.1:9203")
        self.assertEqual(check.status_code, 200)

    @override_settings(ES_DATABASE="http://127.0.0.1:9203")
    def test_basic_view(self):
        fake_request = namedtuple("Request", "GET")
        response = views._find(fake_request({}), "org/test-course/run", 1, "all")
        self.assertFalse(response["results"])
        self.assertEqual(response["old_query"], "*.*")
        self.assertTrue(isinstance(response['data'], SearchResults))

    def tearDown(self):
        self.stub.stop()
