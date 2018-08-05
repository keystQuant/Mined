import pytest

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient


class ExampleTestCase(TestCase):

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def test_TestAPIView_works_as_expected(self):
        response = self.client.get('/mined-test/', format='json')
        """
        dir(response) ==> ['__bytes__', '__class__', '__contains__', '__delattr__', '__delitem__', '__dict__',
        '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__',
        '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__lt__', '__module__', '__ne__',
        '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__',
        '__subclasshook__', '__weakref__', '_charset', '_closable_objects', '_container', '_content_type_for_repr',
        '_convert_to_charset', '_dont_enforce_csrf_checks', '_handler_class', '_headers', '_json', '_reason_phrase',
        'charset', 'client', 'close', 'closed', 'content', 'context', 'cookies', 'delete_cookie', 'flush', 'get', 'getvalue',
        'has_header', 'items', 'json', 'make_bytes', 'readable', 'reason_phrase', 'request', 'resolver_match', 'seekable',
        'serialize', 'serialize_headers', 'set_cookie', 'set_signed_cookie', 'setdefault', 'status_code', 'streaming', 'tell',
        'templates', 'writable', 'write', 'writelines', 'wsgi_request']
        """
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), { 'status': 'SUCCESS' })
