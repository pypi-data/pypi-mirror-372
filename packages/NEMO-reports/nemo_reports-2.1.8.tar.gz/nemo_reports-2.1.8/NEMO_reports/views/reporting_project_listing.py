import datetime

from NEMO.models import AccountType, Project, ProjectDiscipline, ProjectType
from NEMO.typing import QuerySetType
from NEMO.utilities import format_datetime
from NEMO.views.customization import ProjectsAccountsCustomization
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_GET

from NEMO_reports.views.reporting import (
    DEFAULT_PARAMETER_LIST,
    DataDisplayTable,
    ReportingParameters,
    SummaryDisplayTable,
    billing_installed,
    get_department,
    get_institution,
    get_institution_type,
    get_month_range,
    get_monthly_rule,
    get_rate_category,
    get_report_dict,
    report_export,
    reporting_dictionary,
)


@login_required
@permission_required(get_report_dict()["project_listing"]["permission"])
@require_GET
def project_listing(request):
    param_names = DEFAULT_PARAMETER_LIST + ["show_inactive_projects"]
    params = ReportingParameters(request, param_names, default_end_date=datetime.datetime.now().astimezone())
    data = DataDisplayTable()
    summary = SummaryDisplayTable()

    if not params.errors:
        start, end = params.start, params.end
        split_by_month = params.get_bool("split_by_month")
        cumulative_count = params.get_bool("cumulative_count")
        monthly_start = None
        if cumulative_count:
            split_by_month = True
            monthly_start, monthly_end = get_month_range(start)

        RateCategory = get_rate_category()
        InstitutionType = get_institution_type()
        Institution = get_institution()
        Department = get_department()

        if params.get_bool("detailed_data"):
            data.headers = [
                ("name", "Name"),
                ("application_identifier", ProjectsAccountsCustomization.get("project_application_identifier_name")),
                ("active", "Active"),
            ]

            if ProjectType.objects.exists():
                data.add_header(("project_types", "Project type"))
            data.add_header(("account_name", "Account"))
            if AccountType.objects.exists():
                data.add_header(("account_type", "Account type"))
            if ProjectDiscipline.objects.exists():
                data.add_header(("discipline", "Discipline"))

            if billing_installed():
                if RateCategory and RateCategory.objects.exists():
                    data.add_header(("rate_category", "Rate category"))
                if Institution and Institution.objects.exists():
                    data.add_header(("institution_name", "Institution"))
                    data.add_header(("institution_type", "Institution type"))
                    data.add_header(("institution_state", "Institution state"))
                    data.add_header(("institution_country", "Institution country"))
                    data.add_header(("institution_zip", "Institution zipcode"))
                if Department and Department.objects.exists():
                    data.add_header(("department", "Department"))
            data.add_header(("start_date", "Start date"))
            if billing_installed():
                data.add_header(("expiration_date", "Expiration date"))
                data.add_header(("no_charge", "No charge"))
            data.add_header(("pis", "PI(s)"))

            projects = get_projects(params.get_bool("show_inactive_projects"), start, end)
            for project in projects:
                data_row = {
                    "name": project.name,
                    "active": project.active,
                    "application_identifier": project.application_identifier,
                    "project_types": ", ".join([project_type.name for project_type in project.project_types.all()]),
                    "account_name": project.account.name,
                    "account_type": project.account.type,
                    "discipline": project.discipline,
                    "start_date": (
                        format_datetime(project.start_date, "SHORT_DATE_FORMAT") if project.start_date else ""
                    ),
                    "pis": ", ".join([manager.get_name() for manager in project.manager_set.all()]),
                }
                if billing_installed():
                    billing_details = getattr(project, "projectbillingdetails")
                    if billing_details:
                        data_row["name"] = billing_details.name
                        data_row["expiration_date"] = (
                            format_datetime(billing_details.expires_on, "SHORT_DATE_FORMAT")
                            if billing_details.expires_on
                            else None
                        )
                        data_row["rate_category"] = billing_details.category.name if billing_details.category else None
                        data_row["department"] = billing_details.department
                        institution = billing_details.institution
                        if institution:
                            data_row["institution_name"] = institution.name
                            data_row["institution_type"] = institution.institution_type
                            data_row["institution_state"] = institution.state
                            data_row["institution_country"] = institution.get_country_display()
                            data_row["institution_zip"] = institution.zip_code

                data.add_row(data_row)
            data.rows.sort(key=lambda x: x["start_date"])

        summary.add_header(("item", "Item"))
        summary.add_row({"item": "Projects"})
        if ProjectType.objects.exists():
            summary.add_row({"item": "By project type"})
            for project_type in ProjectType.objects.all():
                summary.add_row({"item": f"{project_type.name}"})
            summary.add_row({"item": "N/A"})
        if ProjectDiscipline.objects.exists():
            summary.add_row({"item": "By project discipline"})
            for discipline in ProjectDiscipline.objects.all():
                summary.add_row({"item": f"{discipline.name}"})
            summary.add_row({"item": "N/A"})
        if AccountType.objects.exists():
            summary.add_row({"item": "By account type"})
            for account_type in AccountType.objects.all():
                summary.add_row({"item": f"{account_type.name}"})
            summary.add_row({"item": "N/A"})
        if RateCategory and RateCategory.objects.exists():
            summary.add_row({"item": "By project rate category"})
            for category in RateCategory.objects.all():
                summary.add_row({"item": f"{category.name}"})
            summary.add_row({"item": "N/A"})
        if Institution and Institution.objects.exists():
            summary.add_row({"item": "By institution"})
            for institution in Institution.objects.all():
                summary.add_row({"item": f"{institution.name}"})
            summary.add_row({"item": "N/A"})
        if InstitutionType and InstitutionType.objects.exists():
            summary.add_row({"item": "By institution type"})
            for institution_type in InstitutionType.objects.all():
                summary.add_row({"item": f"{institution_type.name}"})
            summary.add_row({"item": "N/A"})

        if split_by_month:
            for month in get_monthly_rule(start, end):
                month_key = f"month_{month.strftime('%Y')}_{month.strftime('%m')}"
                summary.add_header((month_key, month.strftime("%b %Y")))
                month_start, month_end = get_month_range(month)
                add_summary_info(params, summary, monthly_start or month_start, month_end, month_key)
        else:
            summary.add_header(("value", "Count"))
            add_summary_info(params, summary, start, end)

        if params.get_bool("export"):
            return report_export([summary, data], "project_listing", start, end)

    dictionary = {
        "data": data,
        "summary": summary,
        "errors": params.errors,
    }

    return render(
        request,
        "NEMO_reports/report_project_listing.html",
        reporting_dictionary("project_listing", params, dictionary),
    )


def add_summary_info(
    parameters: ReportingParameters,
    summary: SummaryDisplayTable,
    start,
    end,
    summary_key=None,
):

    RateCategory = get_rate_category()
    InstitutionType = get_institution_type()
    Institution = get_institution()

    summary_key = summary_key or "value"
    projects = get_projects(parameters.get_bool("show_inactive_projects"), start, end)
    summary.rows[0][summary_key] = len(projects)
    current_row = 1

    if ProjectType.objects.exists():
        for project_type in ProjectType.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(filter(lambda x: project_type in x.project_types.all(), projects))
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(list(filter(lambda x: not x.project_types.exists(), projects)))
        current_row += 1  # For mid table header
    if ProjectDiscipline.objects.exists():
        for discipline in ProjectDiscipline.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(list(filter(lambda x: x.discipline == discipline, projects)))
        current_row += 1
        summary.rows[current_row][summary_key] = len(list(filter(lambda x: x.discipline is None, projects)))
        current_row += 1  # For mid table header
    if AccountType.objects.exists():
        for account_type in AccountType.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(filter(lambda x: x.account.type == account_type, projects))
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(list(filter(lambda x: x.account.type is None, projects)))
        current_row += 1  # For mid table header
    if RateCategory and RateCategory.objects.exists():
        for category in RateCategory.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(
                    filter(
                        lambda x: getattr(
                            getattr(x, "projectbillingdetails", None),
                            "category",
                            None,
                        )
                        == category,
                        projects,
                    )
                )
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(
            list(
                filter(
                    lambda x: getattr(
                        getattr(x, "projectbillingdetails", None),
                        "category",
                        None,
                    )
                    is None,
                    projects,
                )
            )
        )
        current_row += 1  # For mid table header
    if Institution and Institution.objects.exists():
        for institution in Institution.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(
                    filter(
                        lambda x: getattr(
                            getattr(x, "projectbillingdetails", None),
                            "institution",
                            None,
                        )
                        == institution,
                        projects,
                    )
                )
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(
            list(
                filter(
                    lambda x: getattr(
                        getattr(x, "projectbillingdetails", None),
                        "institution",
                        None,
                    )
                    is None,
                    projects,
                )
            )
        )
        current_row += 1  # For mid table header
    if InstitutionType and InstitutionType.objects.exists():
        for institution_type in InstitutionType.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(
                    filter(
                        lambda x: getattr(
                            getattr(
                                getattr(x, "projectbillingdetails", None),
                                "institution",
                                None,
                            ),
                            "institution_type",
                            None,
                        )
                        == institution_type,
                        projects,
                    )
                )
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(
            list(
                filter(
                    lambda x: getattr(
                        getattr(
                            getattr(x, "projectbillingdetails", None),  # Safely fetch 'projectbillingdetails'
                            "institution",
                            None,  # Safely fetch 'institution' if 'projectbillingdetails' exists
                        ),
                        "institution_type",
                        None,  # Safely fetch 'institution_type' if 'institution' exists
                    )
                    is None,
                    projects,
                )
            )
        )
        current_row += 1  # For mid table header
    current_row += 1


def get_projects(show_inactive_projects: bool, start_date, end_date) -> QuerySetType[Project]:
    projects = Project.objects.all()
    if not show_inactive_projects:
        projects = projects.filter(active=True)
    if billing_installed():
        # Logic:
        # 1. A project with no start and no end date should always be included.
        # 2. A project with both a start and an end date should overlap with the given date range.
        # 3. A project with only a start date should have its start date before (or equal to) the end of the date range.
        # 4. A project with only an end date should have its end date after (or equal to) the start of the date range.
        projects = projects.filter(
            Q(start_date__isnull=True, projectbillingdetails__expires_on__isnull=True)  # Case 1
            | Q(start_date__lte=end_date, projectbillingdetails__expires_on__gte=start_date)  # Case 2
            | Q(start_date__lte=end_date, projectbillingdetails__expires_on__isnull=True)  # Case 3
            | Q(projectbillingdetails__expires_on__gte=start_date, start_date__isnull=True)  # Case 4
        )
        projects = projects.prefetch_related(
            "projectbillingdetails",
            "projectbillingdetails__category",
            "projectbillingdetails__institution",
            "projectbillingdetails__institution__institution_type",
        )
    else:
        # No billing, no expiration date
        projects = projects.filter(Q(start_date__isnull=True) | Q(start_date__lte=end_date))  # Case 2
    projects = projects.prefetch_related("manager_set", "project_types", "account", "account__type", "discipline")
    return projects
