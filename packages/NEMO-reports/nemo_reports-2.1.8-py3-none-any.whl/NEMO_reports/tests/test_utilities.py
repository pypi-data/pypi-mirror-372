from django.test import TestCase
from requests import Response


def test_response_is_url(test_case: TestCase, response: Response, url: str = "/"):
    test_case.assertEqual(response.status_code, 200)
    test_case.assertEqual(response.request["PATH_INFO"], url)
