import datetime
from typing import Any, List, Union

from NEMO.models import (
    Account,
    AccountType,
    Area,
    AreaAccessRecord,
    ConsumableWithdraw,
    Project,
    ProjectDiscipline,
    ProjectType,
    Reservation,
    StaffCharge,
    Tool,
    TrainingSession,
    UsageEvent,
    User,
)
from NEMO.utilities import queryset_search_filter
from NEMO.views.api_billing import (
    BillableItem,
    billable_items_area_access_records,
    billable_items_consumable_withdrawals,
    billable_items_missed_reservations,
    billable_items_staff_charges,
    billable_items_training_sessions,
    billable_items_usage_events,
    get_minutes_between_dates,
)
from NEMO.views.customization import ProjectsAccountsCustomization
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F, Q, QuerySet, Sum
from django.shortcuts import render
from django.views.decorators.http import require_GET

from NEMO_reports.views.reporting import (
    ACTIVITIES_PARAMETER_LIST,
    DEFAULT_PARAMETER_LIST,
    DataDisplayTable,
    ITEM_PARAMETER,
    ReportingParameters,
    SummaryDisplayTable,
    USER_PARAMETER,
    area_access,
    consumable_withdraws,
    get_core_facility,
    get_institution,
    get_institution_type,
    get_month_range,
    get_monthly_rule,
    get_rate_category,
    get_report_dict,
    missed_reservations,
    report_export,
    reporting_dictionary,
    staff_charges,
    training_sessions,
    usage_events,
)


@login_required
@permission_required(get_report_dict()["facility_usage"]["permission"])
@require_GET
def user_search(request):
    return queryset_search_filter(User.objects.all(), ["first_name", "last_name", "username"], request)


@login_required
@permission_required(get_report_dict()["facility_usage"]["permission"])
@require_GET
def project_search(request):
    return queryset_search_filter(Project.objects.all(), ["name", "application_identifier"], request)


@login_required
@permission_required(get_report_dict()["facility_usage"]["permission"])
@require_GET
def account_search(request):
    return queryset_search_filter(Account.objects.all(), ["name"], request)


@login_required
@permission_required(get_report_dict()["facility_usage"]["permission"])
@require_GET
def facility_usage(request):
    param_names = DEFAULT_PARAMETER_LIST + ACTIVITIES_PARAMETER_LIST
    params = ReportingParameters(request, param_names, USER_PARAMETER + ITEM_PARAMETER)
    data = DataDisplayTable()
    summary = SummaryDisplayTable()
    user_ids = params.get_dict().get("user_ids")
    project_ids = params.get_dict().get("project_ids")
    account_ids = params.get_dict().get("account_ids")
    tool_ids = params.get_dict().get("tool_ids")
    area_ids = params.get_dict().get("area_ids")

    if not params.errors:
        start, end = params.start, params.end
        split_by_month = params.get_bool("split_by_month")
        cumulative_count = params.get_bool("cumulative_count")
        charge_count = params.get_bool("charge_count")
        # Make sure we are not getting incompatible charge types with tool/area selection
        if tool_ids:
            setattr(params, "area_access", "off")
            setattr(params, "staff_charges", "off")
        if area_ids:
            setattr(params, "tool_usage", "off")
            setattr(params, "training", "off")
            setattr(params, "staff_charges", "off")
        monthly_start = None
        if cumulative_count:
            split_by_month = True
            monthly_start, monthly_end = get_month_range(start)

        rate_categories = get_rate_category().objects.all() if get_rate_category() else []
        core_facilities = get_core_facility().objects.all() if get_core_facility() else []
        institution_types = get_institution_type().objects.all() if get_institution_type() else []
        Institution = get_institution()

        total_billables = []

        if params.get_bool("detailed_data"):
            data.headers = [
                ("type", "Type"),
                ("user", "Username"),
                ("staff", "Staff"),
                ("project", "Project"),
                ("project_identifier", ProjectsAccountsCustomization.get("project_application_identifier_name")),
            ]
            if ProjectType.objects.exists():
                project_type_label = (
                    "Project types"
                    if ProjectsAccountsCustomization.get_bool("project_type_allow_multiple")
                    else "Project type"
                )
                data.add_header(("project_types", project_type_label))
            data.headers += [
                ("account", "Account"),
                ("start", "Start"),
                ("end", "End"),
                ("item", "Item"),
                ("details", "Details"),
                ("duration", "Quantity"),
                ("onsite", "On-site"),
            ]

            if core_facilities:
                data.add_header(("core_facility", "Core Facility"))
            if ProjectDiscipline.objects.exists():
                data.add_header(("discipline", "Discipline"))
            if AccountType.objects.exists():
                data.add_header(("account_type", "Account type"))
            if rate_categories:
                data.add_header(("rate_category", "Rate category"))
            if Institution and Institution.objects.exists():
                data.add_header(("institution_name", "Institution Name"))
                data.add_header(("institution_type", "Institution Type"))

            total_value, total_billables = get_facility_usage_value_and_data(
                params, start, end, core_facilities, data=True
            )
            for billable in total_billables:
                project = Project.objects.get(pk=billable.project_id) if getattr(billable, "project_id", None) else None
                project_billing_details = (
                    project.projectbillingdetails if project and hasattr(project, "projectbillingdetails") else None
                )
                institution = project_billing_details.institution if project_billing_details else None
                project_types = project.project_types.all() if project else []
                data_row = {
                    "type": billable.type,
                    "user": billable.username,
                    "staff": billable.staff.username if billable.staff else "",
                    "project": project or "N/A",
                    "project_identifier": project.application_identifier if project else "N/A",
                    "project_types": ", ".join([project_type.name for project_type in project_types]),
                    "account": project.account.name if project else "N/A",
                    "start": billable.start,
                    "end": billable.end,
                    "details": billable.details,
                    "item": billable.name if billable.type != "staff_charge" else None,
                    "duration": billable.timedelta if billable.type != "consumable" else billable.quantity,
                    "onsite": not billable.remote,
                    "core_facility": billable.core_facility,
                    "discipline": project.discipline.name if project and project.discipline else "N/A",
                    "account_type": project.account.type.name if project and project.account.type else "N/A",
                    "institution_name": institution.name if institution else "N/A",
                    "institution_type": (
                        institution.institution_type.name if institution and institution.institution_type else "N/A"
                    ),
                    "rate_category": (
                        project_billing_details.category.name
                        if project_billing_details and project_billing_details.category
                        else "N/A"
                    ),
                }
                data.add_row(data_row)
            data.rows.sort(key=lambda x: x["end"])

        summary.add_header(("item", "Item"))
        summary.add_row({"item": "Facility usage"})
        if core_facilities:
            summary.add_row({"item": "By core facility"})
            for core_facility in core_facilities:
                summary.add_row({"item": f"{core_facility.name}"})
            summary.add_row({"item": "N/A"})
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
        if rate_categories:
            summary.add_row({"item": "By project rate category"})
            for category in rate_categories:
                summary.add_row({"item": f"{category.name}"})
        if institution_types:
            summary.add_row({"item": "By institution type"})
            for institution_type in institution_types:
                summary.add_row({"item": f"{institution_type.name}"})
            summary.add_row({"item": "N/A"})
        summary.add_row({"item": "By remote status"})
        summary.add_row({"item": "Remote"})
        summary.add_row({"item": "On-site"})

        # We only summarize per user when a tool/area is selected
        tool_or_area_selected = params.get_dict().get("tool_ids") or params.get_dict().get("area_ids")
        # There is no point in summarizing per user when we are asking for a specific user's data (unless there is more than one)
        split_by_users = tool_or_area_selected and (
            not params.get_dict().get("user_ids") or len(params.get_dict().get("user_ids")) > 1
        )
        all_users = []
        if split_by_users:
            if not total_billables:
                # Only re-fetch all the data if we haven't already
                all_value, total_billables = get_facility_usage_value_and_data(
                    params, start, end, core_facilities, data=True
                )
            all_users = list({billable.username for billable in total_billables})
            if all_users:
                all_users.sort()
                summary.add_row({"item": "By user"})
                for username in all_users:
                    summary.add_row({"item": username})

        if split_by_month:
            for month in get_monthly_rule(start, end):
                month_key = f"month_{month.strftime('%Y')}_{month.strftime('%m')}"
                summary.add_header((month_key, month.strftime("%b %Y")))
                month_start, month_end = get_month_range(month)
                add_summary_info(
                    params,
                    summary,
                    monthly_start or month_start,
                    month_end,
                    core_facilities,
                    rate_categories,
                    institution_types,
                    month_key,
                )
                if all_users:
                    month_value, month_billables = get_facility_usage_value_and_data(
                        params, month_start, month_end, core_facilities, data=True
                    )
                    add_value_split_by_user(summary, all_users, month_billables, charge_count, month_key)
        else:
            value_label = "Charges" if charge_count else "Time"
            summary.add_header(("value", value_label))
            add_summary_info(params, summary, start, end, core_facilities, rate_categories, institution_types)
            if all_users:
                add_value_split_by_user(summary, all_users, total_billables, charge_count)
        if params.get_bool("export"):
            return report_export([summary, data], "facility_usage", start, end)

    dictionary = {
        "tool_list": Tool.objects.all(),
        "area_list": Area.objects.all(),
        "selected_users": User.objects.filter(id__in=user_ids) if user_ids else None,
        "selected_projects": Project.objects.filter(id__in=project_ids) if project_ids else None,
        "selected_accounts": Account.objects.filter(id__in=account_ids) if account_ids else None,
        "selected_tools": Tool.objects.filter(id__in=tool_ids) if tool_ids else None,
        "selected_areas": Area.objects.filter(id__in=area_ids) if area_ids else None,
        "data": data,
        "summary": summary,
        "errors": params.errors,
    }
    return render(
        request,
        "NEMO_reports/report_facility_usage.html",
        reporting_dictionary("facility_usage", params, dictionary),
    )


def add_value_split_by_user(summary, all_users, total_billables, charge_count, key="value"):
    if all_users:
        # We have to go backwards a bit to find the right row to start at
        current_row = len(summary.rows) - len(all_users)
        for username in all_users:
            # We are using the duration already set on the BillableItem, except for missed reservation where
            # it is set to 1
            if not charge_count:
                user_duration = sum(
                    [
                        (
                            item.quantity
                            if item.type != "missed_reservation"
                            else get_minutes_between_dates(item.start, item.end)
                        )
                        for item in total_billables
                        if item.username == username
                    ]
                )
                summary.rows[current_row][key] = datetime.timedelta(
                    minutes=(float(user_duration) if user_duration else 0)
                )
            else:
                summary.rows[current_row][key] = len([item for item in total_billables if item.username == username])
            current_row += 1


def add_summary_info(
    parameters: ReportingParameters,
    summary: SummaryDisplayTable,
    start,
    end,
    core_facilities,
    rate_categories,
    institution_types,
    summary_key=None,
):
    summary_key = summary_key or "value"
    total_value, billables = get_facility_usage_value_and_data(parameters, start, end, core_facilities)
    summary.rows[0][summary_key] = total_value
    current_row = 1
    if core_facilities:
        for facility in core_facilities:
            current_row += 1
            f_filter = Q(core_facility_id=facility.id)
            f_value, f_billables = get_facility_usage_value_and_data(parameters, start, end, core_facilities, f_filter)
            summary.rows[current_row][summary_key] = f_value
        # Add general (None) subtotal too
        current_row += 1
        f_filter = Q(core_facility_id__isnull=True)
        f_null_value, f_null_billables = get_facility_usage_value_and_data(
            parameters, start, end, core_facilities, f_filter
        )
        summary.rows[current_row][summary_key] = f_null_value
        current_row += 1  # For mid table header
    if ProjectType.objects.exists():
        for project_type in ProjectType.objects.all():
            current_row += 1
            pt_filter = Q(project__project_types__in=[project_type])
            pt_value, pt_billables = get_facility_usage_value_and_data(
                parameters, start, end, core_facilities, pt_filter
            )
            summary.rows[current_row][summary_key] = pt_value
        current_row += 1
        pt_null_filter = Q(project__project_types__isnull=True)
        pt_null_value, pt_null_billables = get_facility_usage_value_and_data(
            parameters, start, end, core_facilities, pt_null_filter
        )
        summary.rows[current_row][summary_key] = pt_null_value
        current_row += 1  # For mid table header
    if ProjectDiscipline.objects.exists():
        for discipline in ProjectDiscipline.objects.all():
            current_row += 1
            p_filter = Q(project__discipline=discipline)
            d_value, d_billables = get_facility_usage_value_and_data(parameters, start, end, core_facilities, p_filter)
            summary.rows[current_row][summary_key] = d_value
        current_row += 1
        p_null_filter = Q(project__discipline__isnull=True)
        d_null_value, d_null_billables = get_facility_usage_value_and_data(
            parameters, start, end, core_facilities, p_null_filter
        )
        summary.rows[current_row][summary_key] = d_null_value
        current_row += 1  # For mid table header
    if AccountType.objects.exists():
        for account_type in AccountType.objects.all():
            current_row += 1
            p_filter = Q(project__account__type=account_type)
            a_value, a_billables = get_facility_usage_value_and_data(parameters, start, end, core_facilities, p_filter)
            summary.rows[current_row][summary_key] = a_value
        current_row += 1
        p_null_filter = Q(project__account__type__isnull=True)
        a_null_value, a_null_billables = get_facility_usage_value_and_data(
            parameters, start, end, core_facilities, p_null_filter
        )
        summary.rows[current_row][summary_key] = a_null_value
        current_row += 1  # For mid table header
    if rate_categories:
        for category in rate_categories:
            current_row += 1
            p_filter = Q(project__projectbillingdetails__category=category)
            r_value, r_billables = get_facility_usage_value_and_data(parameters, start, end, core_facilities, p_filter)
            summary.rows[current_row][summary_key] = r_value
        current_row += 1  # For mid table header
    if institution_types:
        for institution_type in institution_types:
            current_row += 1
            institution_type_filter = Q(project__projectbillingdetails__institution__institution_type=institution_type)
            (
                institution_type_value,
                institution_type_billables,
            ) = get_facility_usage_value_and_data(parameters, start, end, core_facilities, institution_type_filter)
            summary.rows[current_row][summary_key] = institution_type_value
        current_row += 1
        institution_type_null_filter = Q(project__projectbillingdetails__institution__institution_type__isnull=True)
        (
            institution_type_null_value,
            institution_type_null_billables,
        ) = get_facility_usage_value_and_data(parameters, start, end, core_facilities, institution_type_null_filter)
        summary.rows[current_row][summary_key] = institution_type_null_value
        current_row += 1
    current_row += 1
    remote_filter = Q(remote=True)
    remote_value, remote_billables = get_facility_usage_value_and_data(
        parameters, start, end, core_facilities, remote_filter
    )
    summary.rows[current_row][summary_key] = remote_value
    current_row += 1
    onsite_filter = Q(remote=False)
    onsite_value, onsite_billables = get_facility_usage_value_and_data(
        parameters, start, end, core_facilities, onsite_filter
    )
    summary.rows[current_row][summary_key] = onsite_value


def get_facility_usage_value_and_data(
    params: ReportingParameters,
    start: datetime.datetime,
    end: datetime.datetime,
    core_facilities,
    extra_filter: Q = Q(),
    data: bool = False,
) -> (Any, List[BillableItem]):
    # Returns total value (duration or charge count) and data (if the data parameter is True)
    # This allows us to use filtering and aggregate and speed up the process
    # greatly if individual data is not needed.
    charge_count = params.get_bool("charge_count")
    total_value = datetime.timedelta(0) if not charge_count else 0
    billables = []
    user_ids = params.get_dict().get("user_ids")
    project_ids = params.get_dict().get("project_ids")
    account_ids = params.get_dict().get("account_ids")
    tool_ids = params.get_dict().get("tool_ids")
    area_ids = params.get_dict().get("area_ids")
    annotate_core_facilities = bool(core_facilities)
    if user_ids:
        extra_filter &= Q(customer_id__in=user_ids)
    if project_ids:
        extra_filter &= Q(project_id__in=project_ids)
    if account_ids:
        extra_filter &= Q(project__account_id__in=account_ids)
    if params.get_bool("tool_usage", "on"):
        tool_usages = usage_events(start, end, annotate_core_facilities).annotate(timedelta=F("end") - F("start"))
        if extra_filter:
            tool_usages = tool_usages.filter(extra_filter)
        if tool_ids:
            tool_usages = tool_usages.filter(tool_id__in=tool_ids)
        total_value += value_for_charges(tool_usages, "timedelta", charge_count)
        if data:
            billables.extend(map(to_billable_items, tool_usages))
    if params.get_bool("area_access", "on"):
        area_records = area_access(start, end, annotate_core_facilities).annotate(timedelta=F("end") - F("start"))
        if extra_filter:
            area_records = area_records.filter(extra_filter)
        if area_ids:
            area_records = area_records.filter(area_id__in=area_ids)
        total_value += value_for_charges(area_records, "timedelta", charge_count)
        if data:
            billables.extend(map(to_billable_items, area_records))
    if params.get_bool("staff_charges", "on"):
        staff_work = staff_charges(start, end, annotate_core_facilities).annotate(timedelta=F("end") - F("start"))
        if extra_filter:
            staff_work = staff_work.filter(extra_filter)
        total_value += value_for_charges(staff_work, "timedelta", charge_count)
        if data:
            billables.extend(map(to_billable_items, staff_work))
    if params.get_bool("consumables", "on"):
        consumable_withdrawals = consumable_withdraws(start, end, annotate_core_facilities)
        if extra_filter:
            consumable_withdrawals = consumable_withdrawals.filter(extra_filter)
        if charge_count:
            total_value += consumable_withdrawals.count()
        if data:
            billables.extend(map(to_billable_items, consumable_withdrawals))
    if params.get_bool("training", "on"):
        trainings = training_sessions(start, end, annotate_core_facilities)
        if extra_filter:
            trainings = trainings.filter(extra_filter)
        if tool_ids:
            trainings = trainings.filter(tool_id__in=tool_ids)
        total_value += value_for_charges(trainings, "duration", charge_count, in_minutes=True)
        if data:
            billables.extend(map(to_billable_items, trainings))
    if params.get_bool("missed_reservations", "on"):
        reservations = missed_reservations(start, end, annotate_core_facilities).annotate(
            timedelta=F("end") - F("start")
        )
        if extra_filter:
            reservations = reservations.filter(extra_filter)
        if tool_ids and area_ids:
            reservations = reservations.filter(Q(tool_id__in=tool_ids) | Q(area_id__in=area_ids))
        elif tool_ids:
            reservations = reservations.filter(tool_id__in=tool_ids)
        elif area_ids:
            reservations = reservations.filter(area_id__in=area_ids)
        total_value += value_for_charges(reservations, "timedelta", charge_count)
        if data:
            billables.extend(map(to_billable_items, reservations))
    return total_value, billables


def to_billable_items(
    obj: Union[UsageEvent, AreaAccessRecord, TrainingSession, StaffCharge, Reservation],
) -> BillableItem:
    billable = None
    if isinstance(obj, UsageEvent):
        billable = billable_items_usage_events([obj])[0]
    elif isinstance(obj, AreaAccessRecord):
        billable = billable_items_area_access_records([obj])[0]
    elif isinstance(obj, Reservation):
        billable = billable_items_missed_reservations([obj])[0]
    elif isinstance(obj, StaffCharge):
        billable = billable_items_staff_charges([obj])[0]
    elif isinstance(obj, ConsumableWithdraw):
        billable = billable_items_consumable_withdrawals([obj])[0]
    elif isinstance(obj, TrainingSession):
        billable = billable_items_training_sessions([obj])[0]
    if billable:
        # This was added by the annotate function
        billable.timedelta = getattr(obj, "timedelta", None) or (
            datetime.timedelta(minutes=obj.duration) if isinstance(obj, TrainingSession) else datetime.timedelta(0)
        )
        billable.core_facility = getattr(obj, "core_facility_name", None)
        billable.remote = getattr(obj, "remote", None)
        add_extra_billable_info(billable, obj)
    return billable


# Remove when those things are added in NEMO itself
def add_extra_billable_info(billable: BillableItem, obj):
    billable.staff = None
    if isinstance(obj, UsageEvent):
        if obj.operator != obj.user:
            billable.staff = obj.operator
            billable.details = "Work performed by on user's behalf"
    elif isinstance(obj, AreaAccessRecord):
        if obj.staff_charge:
            billable.staff = obj.staff_charge.staff_member
            billable.details = "Area accessed on user's behalf"
    elif isinstance(obj, Reservation):
        if obj.user != obj.creator:
            billable.staff = obj.creator
    elif isinstance(obj, StaffCharge):
        billable.staff = obj.staff_member
        billable.name = "Work performed on behalf of user"
    elif isinstance(obj, ConsumableWithdraw):
        billable.staff = obj.merchant
    elif isinstance(obj, TrainingSession):
        billable.details = f"{obj.get_type_display()} training"
        billable.staff = obj.trainer


def value_for_charges(charges_qs: QuerySet, field_name: str, charge_count: bool = False, in_minutes: bool = False):
    # Return the sum of the field_name or number of events
    if not charge_count:
        value = charges_qs.aggregate(Sum(field_name))[field_name + "__sum"]
        return datetime.timedelta(minutes=value or 0) if in_minutes else (value or datetime.timedelta(0))
    else:
        return charges_qs.count()
