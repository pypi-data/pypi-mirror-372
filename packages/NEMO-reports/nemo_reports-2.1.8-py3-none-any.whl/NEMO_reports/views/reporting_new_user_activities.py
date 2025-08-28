import datetime
from typing import List

from NEMO.models import (
    AccountType,
    AreaAccessRecord,
    ConsumableWithdraw,
    ProjectDiscipline,
    Reservation,
    StaffCharge,
    TrainingSession,
    UsageEvent,
    User,
)
from NEMO.utilities import beginning_of_the_day, end_of_the_day
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import CharField, OuterRef, Subquery, Value
from django.shortcuts import render
from django.views.decorators.http import require_GET

from NEMO_reports.views.reporting import (
    ACTIVITIES_PARAMETER_LIST,
    DEFAULT_PARAMETER_LIST,
    DataDisplayTable,
    ReportingParameters,
    SummaryDisplayTable,
    billing_installed,
    get_core_facility,
    get_institution,
    get_institution_type,
    get_month_range,
    get_monthly_rule,
    get_project_to_exclude_filter,
    get_rate_category,
    get_report_dict,
    report_export,
    reporting_dictionary,
)


@login_required
@permission_required(get_report_dict()["new_users"]["permission"])
@require_GET
def new_users(request):
    param_names = DEFAULT_PARAMETER_LIST + ACTIVITIES_PARAMETER_LIST + ["during_date_range"]
    params = ReportingParameters(request, param_names)
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
        CoreFacility = get_core_facility()
        InstitutionType = get_institution_type()
        Institution = get_institution()

        if params.get_bool("detailed_data"):
            data.headers = [
                ("first", "First name"),
                ("last", "Last name"),
                ("username", "Username"),
                ("first_activity", "First activity"),
                ("project", "Project"),
            ]

            if billing_installed():
                if CoreFacility and CoreFacility.objects.exists():
                    data.add_header(("core_facility", "Core Facility"))
                if RateCategory and RateCategory.objects.exists():
                    data.add_header(("rate_category", "Rate category"))
                if Institution and Institution.objects.exists():
                    data.add_header(("institution_name", "Institution Name"))
                    data.add_header(("institution_type", "Institution Type"))
            if ProjectDiscipline.objects.exists():
                data.add_header(("discipline", "Discipline"))
            if AccountType.objects.exists():
                data.add_header(("account_type", "Account type"))

            new_users = get_first_activities_and_data(params, start, end)
            for user in new_users:
                data_row = {
                    "first": user.first_name,
                    "last": user.last_name,
                    "username": user.username,
                    "first_activity": getattr(user, "first_activity", None),
                    "project": getattr(user, "first_activity_project", None),
                    "discipline": getattr(user, "first_activity_discipline", None),
                    "account_type": getattr(user, "first_activity_account_type", None),
                }
                if billing_installed():
                    data_row["institution_name"] = getattr(user, "first_activity_institution_name", None)
                    data_row["institution_type"] = getattr(user, "first_activity_institution_type", None)
                    data_row["rate_category"] = getattr(user, "first_activity_rate_category", None)
                    data_row["core_facility"] = getattr(user, "first_activity_core_facility", None)

                data.add_row(data_row)
            data.rows.sort(key=lambda x: x["first_activity"])

        summary.add_header(("item", "Item"))
        summary.add_row({"item": "New users"})
        if CoreFacility and CoreFacility.objects.exists():
            summary.add_row({"item": "By core facility"})
            for facility in CoreFacility.objects.all():
                summary.add_row({"item": f"{facility.name}"})
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
            summary.add_header(("value", "Value"))
            add_summary_info(params, summary, start, end)

        if params.get_bool("export"):
            return report_export([summary, data], "active_users", start, end)

    dictionary = {
        "data": data,
        "summary": summary,
        "errors": params.errors,
    }

    return render(
        request,
        "NEMO_reports/report_new_users.html",
        reporting_dictionary("new_users", params, dictionary),
    )


def add_summary_info(
    parameters: ReportingParameters,
    summary: SummaryDisplayTable,
    start,
    end,
    summary_key=None,
):

    RateCategory = get_rate_category()
    CoreFacility = get_core_facility()
    InstitutionType = get_institution_type()
    Institution = get_institution()

    summary_key = summary_key or "value"
    users = get_first_activities_and_data(parameters, start, end)
    summary.rows[0][summary_key] = len(users)
    current_row = 1

    if CoreFacility and CoreFacility.objects.exists():
        for facility in CoreFacility.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(filter(lambda x: x.first_activity_core_facility == facility.name, users))
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(
            list(filter(lambda x: x.first_activity_core_facility is None, users))
        )
        current_row += 1  # For mid table header
    if ProjectDiscipline.objects.exists():
        for discipline in ProjectDiscipline.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(filter(lambda x: x.first_activity_discipline == discipline.name, users))
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(list(filter(lambda x: x.first_activity_discipline is None, users)))
        current_row += 1  # For mid table header
    if AccountType.objects.exists():
        for account_type in AccountType.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(filter(lambda x: x.first_activity_account_type == account_type.name, users))
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(
            list(filter(lambda x: x.first_activity_account_type is None, users))
        )
        current_row += 1  # For mid table header
    if RateCategory and RateCategory.objects.exists():
        for category in RateCategory.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(filter(lambda x: x.first_activity_rate_category == category.name, users))
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(
            list(filter(lambda x: x.first_activity_rate_category is None, users))
        )
        current_row += 1  # For mid table header
    if Institution and Institution.objects.exists():
        for institution in Institution.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(filter(lambda x: x.first_activity_institution_name == institution.name, users))
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(
            list(filter(lambda x: x.first_activity_institution_name is None, users))
        )
        current_row += 1  # For mid table header
    if InstitutionType and InstitutionType.objects.exists():
        for institution_type in InstitutionType.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = len(
                list(filter(lambda x: x.first_activity_institution_type == institution_type.name, users))
            )
        current_row += 1
        summary.rows[current_row][summary_key] = len(
            list(filter(lambda x: x.first_activity_institution_type is None, users))
        )
        current_row += 1  # For mid table header
    current_row += 1


def get_first_activities_and_data(
    params: ReportingParameters,
    start: datetime.datetime,
    end: datetime.datetime,
) -> List[User]:
    origin_start = params.start
    users = User.objects.all()
    during_date_range = params.get_bool("during_date_range")
    origin_start_datetime = beginning_of_the_day(datetime.datetime.combine(origin_start, datetime.time()))
    start_datetime = beginning_of_the_day(datetime.datetime.combine(start, datetime.time()))
    end_datetime = end_of_the_day(datetime.datetime.combine(end, datetime.time()))
    base_empty_annotations = {}
    for first_type in [
        "first_tool_usage",
        "first_area_access",
        "first_staff_charge",
        "first_training",
        "first_missed_reservation",
        "first_consumable_withdrawal",
        "first_custom_charge",
    ]:
        for first_type_property in [
            "_project",
            "_discipline",
            "_account_type",
            "_core_facility",
            "_rate_category",
            "_institution_name",
            "_institution_type",
        ]:
            base_empty_annotations[first_type + first_type_property] = Value(None, output_field=CharField())
    users = users.annotate(**base_empty_annotations)
    if params.get_bool("tool_usage", "on"):
        first_usage_sub = UsageEvent.objects.filter(user=OuterRef("pk"))
        first_usage_sub = first_usage_sub.exclude(get_project_to_exclude_filter())
        if during_date_range:
            first_usage_sub = first_usage_sub.filter(start__gte=origin_start_datetime)
        first_usage_sub = first_usage_sub.order_by("start")
        users = users.annotate(
            first_tool_usage=Subquery(first_usage_sub.values("start")[:1]),
            first_tool_usage_project=Subquery(first_usage_sub.values("project__name")[:1]),
            first_tool_usage_discipline=Subquery(first_usage_sub.values("project__discipline__name")[:1]),
            first_tool_usage_account_type=Subquery(first_usage_sub.values("project__account__type__name")[:1]),
        )
        if billing_installed():
            users = users.annotate(
                first_tool_usage_core_facility=Subquery(
                    first_usage_sub.values("tool__core_rel__core_facility__name")[:1]
                ),
                first_tool_usage_rate_category=Subquery(
                    first_usage_sub.values("project__projectbillingdetails__category__name")[:1]
                ),
                first_tool_usage_institution_name=Subquery(
                    first_usage_sub.values("project__projectbillingdetails__institution__name")[:1]
                ),
                first_tool_usage_institution_type=Subquery(
                    first_usage_sub.values("project__projectbillingdetails__institution__institution_type__name")[:1]
                ),
            )
    if params.get_bool("area_access", "on"):
        first_access_sub = AreaAccessRecord.objects.filter(customer=OuterRef("pk"))
        first_access_sub = first_access_sub.exclude(get_project_to_exclude_filter())
        if during_date_range:
            first_access_sub = first_access_sub.filter(start__gte=origin_start_datetime)
        first_access_sub = first_access_sub.order_by("start")
        users = users.annotate(
            first_area_access=Subquery(first_access_sub.values("start")[:1]),
            first_area_access_project=Subquery(first_access_sub.values("project__name")[:1]),
            first_area_access_discipline=Subquery(first_access_sub.values("project__discipline__name")[:1]),
            first_area_access_account_type=Subquery(first_access_sub.values("project__account__type__name")[:1]),
        )
        if billing_installed():
            users = users.annotate(
                first_area_access_core_facility=Subquery(
                    first_access_sub.values("area__core_rel__core_facility__name")[:1]
                ),
                first_area_access_rate_category=Subquery(
                    first_access_sub.values("project__projectbillingdetails__category__name")[:1]
                ),
                first_area_access_institution_name=Subquery(
                    first_access_sub.values("project__projectbillingdetails__institution__name")[:1]
                ),
                first_area_access_institution_type=Subquery(
                    first_access_sub.values("project__projectbillingdetails__institution__institution_type__name")[:1]
                ),
            )
    if params.get_bool("staff_charges", "on"):
        first_staff_charge_sub = StaffCharge.objects.filter(customer=OuterRef("pk"))
        first_staff_charge_sub = first_staff_charge_sub.exclude(get_project_to_exclude_filter())
        if during_date_range:
            first_staff_charge_sub = first_staff_charge_sub.filter(start__gte=origin_start_datetime)
        first_staff_charge_sub = first_staff_charge_sub.order_by("start")
        users = users.annotate(
            first_staff_charge=Subquery(first_staff_charge_sub.values("start")[:1]),
            first_staff_charge_project=Subquery(first_staff_charge_sub.values("project__name")[:1]),
            first_staff_charge_discipline=Subquery(first_staff_charge_sub.values("project__discipline__name")[:1]),
            first_staff_charge_account_type=Subquery(first_staff_charge_sub.values("project__account__type__name")[:1]),
        )
        if billing_installed():
            users = users.annotate(
                first_staff_charge_core_facility=Subquery(
                    first_staff_charge_sub.values("core_rel__core_facility__name")[:1]
                ),
                first_staff_charge_rate_category=Subquery(
                    first_staff_charge_sub.values("project__projectbillingdetails__category__name")[:1]
                ),
                first_staff_charge_institution_name=Subquery(
                    first_staff_charge_sub.values("project__projectbillingdetails__institution__name")[:1]
                ),
                first_staff_charge_institution_type=Subquery(
                    first_staff_charge_sub.values(
                        "project__projectbillingdetails__institution__institution_type__name"
                    )[:1]
                ),
            )
    if params.get_bool("training", "on"):
        first_training_sub = TrainingSession.objects.filter(trainee=OuterRef("pk"))
        first_training_sub = first_training_sub.exclude(get_project_to_exclude_filter())
        if during_date_range:
            first_training_sub = first_training_sub.filter(date__gte=origin_start_datetime)
        first_training_sub = first_training_sub.order_by("date")
        users = users.annotate(
            first_training=Subquery(first_training_sub.values("date")[:1]),
            first_training_project=Subquery(first_training_sub.values("project__name")[:1]),
            first_training_discipline=Subquery(first_training_sub.values("project__discipline__name")[:1]),
            first_training_account_type=Subquery(first_training_sub.values("project__account__type__name")[:1]),
        )
        if billing_installed():
            users = users.annotate(
                first_training_core_facility=Subquery(
                    first_training_sub.values("tool__core_rel__core_facility__name")[:1]
                ),
                first_training_rate_category=Subquery(
                    first_training_sub.values("project__projectbillingdetails__category__name")[:1]
                ),
                first_training_institution_name=Subquery(
                    first_training_sub.values("project__projectbillingdetails__institution__name")[:1]
                ),
                first_training_institution_type=Subquery(
                    first_training_sub.values("project__projectbillingdetails__institution__institution_type__name")[:1]
                ),
            )
    if params.get_bool("missed_reservations", "on"):
        first_missed_sub = Reservation.objects.filter(missed=True, user=OuterRef("pk"))
        first_missed_sub = first_missed_sub.exclude(get_project_to_exclude_filter())
        if during_date_range:
            first_missed_sub = first_missed_sub.filter(start__gte=origin_start_datetime)
        first_missed_sub = first_missed_sub.order_by("start")
        users = users.annotate(
            first_missed_reservation=Subquery(first_missed_sub.order_by("start").values("start")[:1]),
            first_missed_reservation_project=Subquery(first_missed_sub.values("project__name")[:1]),
            first_missed_reservation_discipline=Subquery(first_missed_sub.values("project__discipline__name")[:1]),
            first_missed_reservation_account_type=Subquery(first_missed_sub.values("project__account__type__name")[:1]),
        )
        if billing_installed():
            users = users.annotate(
                first_missed_reservation_rate_category=Subquery(
                    first_missed_sub.values("project__projectbillingdetails__category__name")[:1]
                ),
                first_missed_reservation_institution_name=Subquery(
                    first_missed_sub.values("project__projectbillingdetails__institution__name")[:1]
                ),
                first_missed_reservation_institution_type=Subquery(
                    first_missed_sub.values("project__projectbillingdetails__institution__institution_type__name")[:1]
                ),
            )
    if params.get_bool("consumables", "on"):
        first_consumable_sub = ConsumableWithdraw.objects.filter(customer=OuterRef("pk"))
        first_consumable_sub = first_consumable_sub.exclude(get_project_to_exclude_filter())
        if during_date_range:
            first_consumable_sub = first_consumable_sub.filter(date__gte=origin_start_datetime)
        first_consumable_sub = first_consumable_sub.order_by("date")
        users = users.annotate(
            first_consumable_withdrawal=Subquery(first_consumable_sub.values("date")[:1]),
            first_consumable_withdrawal_project=Subquery(first_consumable_sub.values("project__name")[:1]),
            first_consumable_withdrawal_discipline=Subquery(
                first_consumable_sub.values("project__discipline__name")[:1]
            ),
            first_consumable_withdrawal_account_type=Subquery(
                first_consumable_sub.values("project__account__type__name")[:1]
            ),
        )
        if billing_installed():
            users = users.annotate(
                first_consumable_withdrawal_core_facility=Subquery(
                    first_consumable_sub.values("consumable__core_rel__core_facility__name")[:1]
                ),
                first_consumable_withdrawal_rate_category=Subquery(
                    first_consumable_sub.values("project__projectbillingdetails__category__name")[:1]
                ),
                first_consumable_withdrawal_institution_name=Subquery(
                    first_consumable_sub.values("project__projectbillingdetails__institution__name")[:1]
                ),
                first_consumable_withdrawal_institution_type=Subquery(
                    first_consumable_sub.values("project__projectbillingdetails__institution__institution_type__name")[
                        :1
                    ]
                ),
            )
    if billing_installed():
        from NEMO_billing.models import CustomCharge

        if params.get_bool("custom_charges", "on"):
            first_custom_sub = CustomCharge.objects.filter(customer=OuterRef("pk"))
            first_custom_sub = first_custom_sub.exclude(get_project_to_exclude_filter())
            if during_date_range:
                first_custom_sub = first_custom_sub.filter(date__gte=origin_start_datetime)
            first_custom_sub = first_custom_sub.order_by("date")
            users = users.annotate(
                first_custom_charge=Subquery(first_custom_sub.values("date")[:1]),
                first_custom_charge_project=Subquery(first_custom_sub.values("project__name")[:1]),
                first_custom_charge_discipline=Subquery(first_custom_sub.values("project__discipline__name")[:1]),
                first_custom_charge_account_type=Subquery(first_custom_sub.values("project__account__type__name")[:1]),
            )
            if billing_installed():
                users = users.annotate(
                    first_custom_charge_core_facility=Subquery(first_custom_sub.values("core_facility__name")[:1]),
                    first_custom_charge_rate_category=Subquery(
                        first_custom_sub.values("project__projectbillingdetails__category__name")[:1]
                    ),
                    first_custom_charge_institution_name=Subquery(
                        first_custom_sub.values("project__projectbillingdetails__institution__name")[:1]
                    ),
                    first_custom_charge_institution_type=Subquery(
                        first_custom_sub.values("project__projectbillingdetails__institution__institution_type__name")[
                            :1
                        ]
                    ),
                )
    for user in users:
        activity_list = [
            user.first_tool_usage,
            user.first_area_access,
            user.first_staff_charge,
            user.first_training,
            user.first_missed_reservation,
            user.first_consumable_withdrawal,
        ]
        if billing_installed():
            activity_list += [user.first_custom_charge]
        user.first_activity = min(
            [act for act in activity_list if act],
            default=None,
        )
        if user.first_activity:
            for activity_type in reversed(
                [
                    "first_tool_usage",
                    "first_area_access",
                    "first_staff_charge",
                    "first_training",
                    "first_missed_reservation",
                    "first_consumable_withdrawal",
                    "first_custom_charge",
                ]
            ):
                if user.first_activity == getattr(user, activity_type, None):
                    for activity_type_type in [
                        "_project",
                        "_discipline",
                        "_account_type",
                        "_core_facility",
                        "_rate_category",
                        "_institution_name",
                        "_institution_type",
                    ]:
                        setattr(
                            user,
                            "first_activity" + activity_type_type,
                            getattr(user, activity_type + activity_type_type, None),
                        )
    return [user for user in users if user.first_activity and start_datetime <= user.first_activity <= end_datetime]
