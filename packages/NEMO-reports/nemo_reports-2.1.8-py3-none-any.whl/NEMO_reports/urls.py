from django.urls import include, path

from NEMO_reports.views import (
    reporting,
    reporting_facilily_usage,
    reporting_new_user_activities,
    reporting_project_listing,
    reporting_project_users,
    reporting_unique_user_prj_acc,
)

urlpatterns = [
    path(
        "reporting/",
        include(
            [
                path("", reporting.reports, name="reporting"),
                path("facility_usage/", reporting_facilily_usage.facility_usage, name="reporting_facility_usage"),
                path(
                    "facility_usage/user_search",
                    reporting_facilily_usage.user_search,
                    name="reporting_facility_usage_user_search",
                ),
                path(
                    "facility_usage/project_search",
                    reporting_facilily_usage.project_search,
                    name="reporting_facility_usage_project_search",
                ),
                path(
                    "facility_usage/account_search",
                    reporting_facilily_usage.account_search,
                    name="reporting_facility_usage_account_search",
                ),
                path("unique_users/", reporting_unique_user_prj_acc.unique_users, name="reporting_unique_users"),
                path("new_users/", reporting_new_user_activities.new_users, name="reporting_new_users"),
                path("project_users/", reporting_project_users.project_users, name="reporting_project_users"),
                path("project_listing/", reporting_project_listing.project_listing, name="reporting_project_listing"),
                path(
                    "unique_user_project/",
                    reporting_unique_user_prj_acc.unique_user_and_project_combinations,
                    name="reporting_unique_user_project",
                ),
                path(
                    "unique_user_account/",
                    reporting_unique_user_prj_acc.unique_user_and_account_combinations,
                    name="reporting_unique_user_account",
                ),
            ]
        ),
    ),
]

if reporting.billing_installed():
    from NEMO_reports.views import reporting_invoice_charges, reporting_invoice_item_charges

    urlpatterns += [
        path("reporting/invoice_charges/", reporting_invoice_charges.invoice_charges, name="reporting_invoice_charges"),
        path(
            "reporting/invoice_item_charges/",
            reporting_invoice_item_charges.invoice_items,
            name="reporting_invoice_item_charges",
        ),
    ]
