from NEMO.models import Account, Project, User
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from NEMO_reports.customizations import ReportsCustomization
from NEMO_reports.tests.test_utilities import test_response_is_url
from NEMO_reports.views.reporting import billing_installed


class TestReports(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(
            username="test_user", first_name="Testy", last_name="McTester", badge_number=1
        )
        project = Project.objects.create(name="excluded_project", account=Account.objects.create(name="acct"))
        ReportsCustomization.set("reports_exclude_projects", project.id)

    def test_master_url(self):
        self.user: User = self.user
        self.client.force_login(self.user)
        response = self.client.get(reverse("reporting"), follow=True)
        test_response_is_url(self, response)
        self.user.user_permissions.add(Permission.objects.get(codename="can_view_unique_users_report"))
        response = self.client.get(reverse("reporting"), follow=True)
        test_response_is_url(self, response, reverse("reporting"))

    def test_unique_users_report(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("reporting_unique_users"), follow=True)
        test_response_is_url(self, response)
        self.user.user_permissions.add(Permission.objects.get(codename="can_view_unique_users_report"))
        response = self.client.get(reverse("reporting_unique_users"), follow=True)
        test_response_is_url(self, response, reverse("reporting_unique_users"))

    def test_unique_user_project_report(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("reporting_unique_user_project"), follow=True)
        test_response_is_url(self, response)
        self.user.user_permissions.add(Permission.objects.get(codename="can_view_unique_user_project_report"))
        response = self.client.get(reverse("reporting_unique_user_project"), follow=True)
        test_response_is_url(self, response, reverse("reporting_unique_user_project"))

    def test_unique_user_account_report(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("reporting_unique_user_account"), follow=True)
        test_response_is_url(self, response)
        self.user.user_permissions.add(Permission.objects.get(codename="can_view_unique_user_account_report"))
        response = self.client.get(reverse("reporting_unique_user_account"), follow=True)
        test_response_is_url(self, response, reverse("reporting_unique_user_account"))

    def test_invoice_charges_report(self):
        if billing_installed():
            self.client.force_login(self.user)
            response = self.client.get(reverse("reporting_invoice_charges"), follow=True)
            test_response_is_url(self, response)
            self.user.user_permissions.add(Permission.objects.get(codename="can_view_invoice_charges_report"))
            response = self.client.get(reverse("reporting_invoice_charges"), follow=True)
            test_response_is_url(self, response, reverse("reporting_invoice_charges"))
        else:
            self.assertRaises(NoReverseMatch, reverse, "reporting_invoice_charges")

    def test_invoice_item_charges_report(self):
        if billing_installed():
            self.client.force_login(self.user)
            response = self.client.get(reverse("reporting_invoice_item_charges"), follow=True)
            test_response_is_url(self, response)
            self.user.user_permissions.add(Permission.objects.get(codename="can_view_invoice_item_charges_report"))
            response = self.client.get(reverse("reporting_invoice_item_charges"), follow=True)
            test_response_is_url(self, response, reverse("reporting_invoice_item_charges"))
        else:
            self.assertRaises(NoReverseMatch, reverse, "reporting_invoice_item_charges")
