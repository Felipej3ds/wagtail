from django.test import TestCase, RequestFactory
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpRequest

from wagtail.models import Page, PageViewRestriction
from wagtail.test.utils import WagtailPageTests

from wagtail.views import authenticate_with_password 

class AuthenticateWithPasswordTests(WagtailPageTests):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="user", password="pass")

        self.root_page = Page.objects.get(id=1)
        self.test_page = self.root_page.add_child(instance=Page(title="Test Page", slug="test-page"))
        self.test_page.save_revision().publish()

        self.restriction = PageViewRestriction.objects.create(
            page=self.test_page,
            restriction_type=PageViewRestriction.PASSWORD,
            password="abc123"
        )

    def simulate_request(self, return_url, is_secure=True):
        request = self.factory.post("/", data={"return_url": return_url})
        request.user = self.user
        request._is_secure = lambda: is_secure
        return authenticate_with_password(request, self.restriction.id, self.test_page.id)

    def test_ct1_invalid_host_and_scheme(self):
        response = self.simulate_request("http://malicious.com", is_secure=True)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

    def test_ct2_invalid_host_valid_scheme(self):
        response = self.simulate_request("https://malicious.com", is_secure=True)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

    def test_ct3_valid_host_invalid_scheme(self):
        host = self.test_page.get_site().hostname
        url = f"http://{host}/some-path"
        response = self.simulate_request(url, is_secure=True)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

    def test_ct4_valid_host_and_scheme(self):
        host = self.test_page.get_site().hostname
        url = f"https://{host}/some-path"
        response = self.simulate_request(url, is_secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)