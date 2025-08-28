import datetime
from collections import defaultdict
from itertools import chain
from typing import Set, Tuple

from NEMO.models import AccountType, Project, ProjectDiscipline, ProjectType, Tool, User, UserType
from NEMO.utilities import format_datetime
from NEMO.views.customization import ProjectsAccountsCustomization
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
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
    get_enabled_user_details_fields,
    get_institution,
    get_institution_type,
    get_month_range,
    get_monthly_rule,
    get_rate_category,
    get_report_dict,
    report_export,
    reporting_dictionary,
    user_details_installed,
)


@login_required
@permission_required(get_report_dict()["project_users"]["permission"])
@require_GET
def project_users(request):
    param_names = DEFAULT_PARAMETER_LIST + [
        "show_inactive_projects",
        "show_inactive_users",
        "show_users_without_projects",
        "user_groups",
        "user_tools",
    ]
    params = ReportingParameters(request, param_names, default_end_date=datetime.datetime.now().astimezone())
    data = DataDisplayTable()
    summary = SummaryDisplayTable()
    selected_groups = Group.objects.filter(id__in=request.GET.getlist("user_groups", []))
    selected_tools = Tool.objects.filter(id__in=request.GET.getlist("user_tools", []))

    if not params.errors:
        start, end = params.start, params.end

        split_by_month = params.get_bool("split_by_month")
        cumulative_count = params.get_bool("cumulative_count")
        user_filter = Q(is_active=True)
        if params.get_bool("show_inactive_users"):
            user_filter = Q()
        if selected_groups:
            user_filter &= Q(groups__in=selected_groups)
        if selected_tools:
            user_filter &= Q(qualifications__in=selected_tools)
        monthly_start = None
        if cumulative_count:
            split_by_month = True
            monthly_start, monthly_end = get_month_range(start)

        RateCategory = get_rate_category()
        InstitutionType = get_institution_type()
        Institution = get_institution()
        Department = get_department()

        user_details_enabled_fields = get_enabled_user_details_fields().items()

        if params.get_bool("detailed_data"):
            data.headers = [
                ("name", "Full name"),
                ("username", "Username"),
                ("email", "Email"),
                ("active", "Active user account"),
                ("created", "User creation date"),
                ("access_expiration_date", "User access expiration date"),
                ("facilities_tutorial", "Facility rules tutorial"),
            ]
            if UserType.objects.exists():
                data.add_header(("user_type", "User type"))
            data.add_header(("qualifications", "Qualifications"))
            if user_details_installed():
                for detail_field_name, detail_field in user_details_enabled_fields:
                    data.add_header((detail_field_name, detail_field.label or detail_field_name.title()))
            data.add_header(("project_name", "Project name")),
            data.add_header(("project_active", "Project active")),
            data.add_header(
                ("application_identifier", ProjectsAccountsCustomization.get("project_application_identifier_name"))
            ),
            if ProjectType.objects.exists():
                project_type_label = (
                    "Project types"
                    if ProjectsAccountsCustomization.get_bool("project_type_allow_multiple")
                    else "Project type"
                )
                data.add_header(("project_types", project_type_label))
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

            user_and_project_list = get_users_and_projects(user_filter, params, start, end)
            for user, project in user_and_project_list:
                data_row = {
                    "name": user.get_name(),
                    "username": user.username,
                    "email": user.email,
                    "active": user.is_active,
                    "created": format_datetime(user.date_joined, "SHORT_DATE_FORMAT"),
                    "access_expiration_date": format_datetime(user.access_expiration, "SHORT_DATE_FORMAT"),
                    "facilities_tutorial": user.training_required,
                    "user_type": user.type,
                    "qualifications": "\n".join([str(tool) for tool in user.qualifications.all()]),
                }
                if project:
                    data_row = {
                        **data_row,
                        "project_name": project.name,
                        "project_active": project.active,
                        "application_identifier": project.application_identifier,
                        "project_types": "\n".join([project_type.name for project_type in project.project_types.all()]),
                        "account_name": project.account.name,
                        "account_type": project.account.type,
                        "discipline": project.discipline,
                        "start_date": (
                            format_datetime(project.start_date, "SHORT_DATE_FORMAT") if project.start_date else ""
                        ),
                        "pis": "\n".join([manager.get_name() for manager in project.manager_set.all()]),
                    }
                if user_details_installed():
                    for detail_field_name, detail_field in user_details_enabled_fields:
                        user_details_value = getattr(getattr(user, "details", None), detail_field_name, None)
                        if detail_field_name == "groups":
                            data_row[detail_field_name] = ", ".join([grp.name for grp in user.groups.all()])
                        else:
                            data_row[detail_field_name] = user_details_value
                if project and billing_installed():
                    billing_details = getattr(project, "projectbillingdetails")
                    if billing_details:
                        data_row["project_name"] = billing_details.name
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
            data.rows.sort(key=lambda x: x["name"])

        summary.add_header(("item", "Item"))
        summary.add_row({"item": "Results"})
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
                add_summary_info(params, summary, monthly_start or month_start, month_end, month_key, user_filter)
        else:
            summary.add_header(("value", "Count"))
            add_summary_info(params, summary, start, end, user_filter=user_filter)

        if params.get_bool("export"):
            return report_export([summary, data], "project_users", start, end)

    dictionary = {
        "data": data,
        "summary": summary,
        "groups": Group.objects.all(),
        "tools": Tool.objects.all(),
        "selected_groups": selected_groups,
        "selected_tools": selected_tools,
        "errors": params.errors,
    }

    return render(
        request,
        "NEMO_reports/report_project_users.html",
        reporting_dictionary("project_users", params, dictionary),
    )


def add_summary_info(
    parameters: ReportingParameters, summary: SummaryDisplayTable, start, end, summary_key=None, user_filter: Q = Q()
):

    RateCategory = get_rate_category()
    InstitutionType = get_institution_type()
    Institution = get_institution()

    summary_key = summary_key or "value"
    user_and_project_list = get_users_and_projects(user_filter, parameters, start, end)
    projects = [x[1] for x in user_and_project_list if x[1]]
    summary.rows[0][summary_key] = len(user_and_project_list)
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


def get_users_and_projects(
    user_filter: Q(), params: ReportingParameters, start_date, end_date
) -> Set[Tuple[User, Project]]:
    show_inactive_projects = params.get_bool("show_inactive_projects")
    show_users_without_projects = params.show_users_without_projects
    user_projects = (
        User.objects.filter(user_filter)
        .filter(date_joined__date__lte=end_date)
        .filter(Q(access_expiration__isnull=True) | Q(access_expiration__gte=start_date))
        .values_list("id", "projects__id")
    )
    user_ids_to_project_ids = defaultdict(list)

    for user_id, project_id in user_projects:
        user_ids_to_project_ids.setdefault(user_id, [])
        if project_id is not None:
            user_ids_to_project_ids[user_id].append(project_id)

    users = User.objects.filter(id__in=user_ids_to_project_ids.keys()).prefetch_related("qualifications", "groups")
    if user_details_installed():
        users = users.prefetch_related("details")
    users = {user.id: user for user in users}
    projects = Project.objects.filter(
        id__in=set(chain.from_iterable(user_ids_to_project_ids.values()))
    ).prefetch_related("manager_set", "project_types", "account", "account__type", "discipline")
    if billing_installed():
        projects = projects.prefetch_related(
            "projectbillingdetails",
            "projectbillingdetails__category",
            "projectbillingdetails__institution",
            "projectbillingdetails__department",
            "projectbillingdetails__institution__institution_type",
        )
    projects = {project.id: project for project in projects}

    results = set()

    # do a first round to remove inactive projects if needed
    if not show_inactive_projects:
        for user_id, project_ids in user_ids_to_project_ids.items():
            user_ids_to_project_ids[user_id] = [project_id for project_id in project_ids if projects[project_id].active]

    for user_id, project_ids in user_ids_to_project_ids.items():
        if project_ids:
            if show_users_without_projects == "false" or not show_users_without_projects:
                for project_id in project_ids:
                    results.add((users[user_id], projects[project_id]))
        else:
            if show_users_without_projects == "false" or show_users_without_projects == "true":
                results.add((users[user_id], None))
    return results
