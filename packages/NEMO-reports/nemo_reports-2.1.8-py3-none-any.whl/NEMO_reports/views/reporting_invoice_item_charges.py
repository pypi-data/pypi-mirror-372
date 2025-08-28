import datetime
from _decimal import Decimal

from NEMO.models import AccountType, AreaAccessRecord, ProjectDiscipline, ProjectType, UsageEvent
from NEMO.views.customization import ProjectsAccountsCustomization
from NEMO_billing.invoices.models import BillableItemType, InvoiceDetailItem
from NEMO_billing.models import Institution, InstitutionType
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import BooleanField, Case, OuterRef, Q, QuerySet, Sum, Value, When
from django.shortcuts import render
from django.views.decorators.http import require_GET

from NEMO_reports.views.reporting import (
    ACTIVITIES_PARAMETER_LIST,
    DEFAULT_PARAMETER_LIST,
    DataDisplayTable,
    ReportingParameters,
    SummaryDisplayTable,
    get_core_facility,
    get_month_range,
    get_monthly_rule,
    get_project_to_exclude_filter,
    get_rate_category,
    get_report_dict,
    report_export,
    reporting_dictionary,
)


@login_required
@permission_required(get_report_dict()["invoice_item_charges"]["permission"])
@require_GET
def invoice_items(request):
    param_names = DEFAULT_PARAMETER_LIST + ACTIVITIES_PARAMETER_LIST
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

        if params.get_bool("detailed_data"):
            data.headers = [
                ("type", "Type"),
                ("name", "Name"),
                ("user", "Username"),
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
                ("invoice", "Invoice"),
                ("start", "Start"),
                ("end", "End"),
                ("duration", "Duration"),
                ("discount", "Discount"),
                ("amount", "Amount"),
                ("onsite", "On-site"),
            ]

            if CoreFacility and CoreFacility.objects.exists():
                data.add_header(("core_facility", "Core Facility"))
            if ProjectDiscipline.objects.exists():
                data.add_header(("discipline", "Discipline"))
            if AccountType.objects.exists():
                data.add_header(("account_type", "Account type"))
            if RateCategory and RateCategory.objects.exists():
                data.add_header(("rate_category", "Rate category"))
            if Institution.objects.exists():
                data.add_header(("institution_name", "Institution Name"))
                data.add_header(("institution_type", "Institution Type"))

            amount, items = get_invoice_items(params, start, end)
            for item in items:
                item: InvoiceDetailItem = item
                project_details = item.invoice.project_details
                project = project_details.project
                project_types = project.project_types.all() if project else []
                data_row = {
                    "type": item.get_item_type_display(),
                    "name": item.name,
                    "user": item.user,
                    "invoice": item.invoice.invoice_number,
                    "project": project,
                    "project_identifier": project.application_identifier,
                    "project_types": ", ".join([project_type.name for project_type in project_types]),
                    "start": item.start,
                    "end": item.end,
                    "duration": item.end - item.start,
                    "discount": item.discount,
                    "amount": item.amount,
                    "onsite": not item.remote,
                    "core_facility": item.core_facility or "N/A",
                    "discipline": project.discipline.name if project and project.discipline else "N/A",
                    "account_type": project.account.type.name if project and project.account.type else "N/A",
                    "institution_name": project_details.institution.name if project_details.institution else "N/A",
                    "institution_type": (
                        project_details.institution.institution_type.name
                        if project_details.institution and project_details.institution.institution_type
                        else "N/A"
                    ),
                }
                if RateCategory and RateCategory.objects.exists():
                    data_row["rate_category"] = project.projectbillingdetails.category.name if project else "N/A"
                data.add_row(data_row)
            data.rows.sort(key=lambda x: x["end"])

        summary.add_header(("item", "Item"))
        summary.add_row({"item": "Total item charges"})
        if CoreFacility and CoreFacility.objects.exists():
            summary.add_row({"item": "By core facility"})
            for core_facility in CoreFacility.objects.all():
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
        if RateCategory and RateCategory.objects.exists():
            summary.add_row({"item": "By project rate category"})
            for category in RateCategory.objects.all():
                summary.add_row({"item": f"{category.name}"})
        if InstitutionType.objects.exists():
            summary.add_row({"item": "By institution type"})
            for institution_type in InstitutionType.objects.all():
                summary.add_row({"item": f"{institution_type.name}"})
            summary.add_row({"item": "N/A"})
        summary.add_row({"item": "By remote status"})
        summary.add_row({"item": "Remote"})
        summary.add_row({"item": "On-site"})

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
            return report_export([summary, data], "invoice_item_charges", start, end)

    dictionary = {
        "data": data,
        "summary": summary,
        "errors": params.errors,
    }

    return render(
        request,
        "NEMO_reports/report_active_users.html",
        reporting_dictionary("invoice_item_charges", params, dictionary),
    )


def add_summary_info(parameters: ReportingParameters, summary: SummaryDisplayTable, start, end, summary_key=None):
    RateCategory = get_rate_category()
    CoreFacility = get_core_facility()
    summary_key = summary_key or "value"
    amount, items = get_invoice_items(parameters, start, end)
    summary.rows[0][summary_key] = amount
    current_row = 1
    if CoreFacility and CoreFacility.objects.exists():
        for facility in CoreFacility.objects.all():
            current_row += 1
            c_amount, c_items = get_invoice_items(parameters, start, end, Q(core_facility=facility.name))
            summary.rows[current_row][summary_key] = c_amount
        # Add general (None) subtotal too
        current_row += 1
        c_null_amount, c_null_items = get_invoice_items(parameters, start, end, Q(core_facility__isnull=True))
        summary.rows[current_row][summary_key] = c_null_amount
        current_row += 1  # For mid table header
    if ProjectType.objects.exists():
        for project_type in ProjectType.objects.all():
            current_row += 1
            pt_amount, pt_items = get_invoice_items(
                parameters, start, end, Q(invoice__project_details__project__project_types__in=[project_type])
            )
            summary.rows[current_row][summary_key] = pt_amount
        current_row += 1
        pt_null_amount, pt_null_items = get_invoice_items(
            parameters, start, end, Q(invoice__project_details__project__project_types__isnull=True)
        )
        summary.rows[current_row][summary_key] = pt_null_amount
        current_row += 1  # For mid table header
    if ProjectDiscipline.objects.exists():
        for discipline in ProjectDiscipline.objects.all():
            current_row += 1
            d_amount, d_items = get_invoice_items(
                parameters, start, end, Q(invoice__project_details__project__discipline=discipline)
            )
            summary.rows[current_row][summary_key] = d_amount
        current_row += 1
        d_null_amount, d_null_items = get_invoice_items(
            parameters, start, end, Q(invoice__project_details__project__discipline__isnull=True)
        )
        summary.rows[current_row][summary_key] = d_null_amount
        current_row += 1  # For mid table header
    if AccountType.objects.exists():
        for account_type in AccountType.objects.all():
            current_row += 1
            a_amount, a_items = get_invoice_items(
                parameters, start, end, Q(invoice__project_details__project__account__type=account_type)
            )
            summary.rows[current_row][summary_key] = a_amount
        current_row += 1
        a_null_amount, a_null_items = get_invoice_items(
            parameters, start, end, Q(invoice__project_details__project__account__type__isnull=True)
        )
        summary.rows[current_row][summary_key] = a_null_amount
        current_row += 1  # For mid table header
    if RateCategory and RateCategory.objects.exists():
        for category in RateCategory.objects.all():
            current_row += 1
            r_amount, r_items = get_invoice_items(
                parameters, start, end, Q(invoice__project_details__category=category)
            )
            summary.rows[current_row][summary_key] = r_amount
        current_row += 1  # For mid table header
    if InstitutionType and InstitutionType.objects.exists():
        for institution_type in InstitutionType.objects.all():
            current_row += 1
            institution_type_amount, institution_type_items = get_invoice_items(
                parameters, start, end, Q(invoice__project_details__institution__institution_type=institution_type)
            )
            summary.rows[current_row][summary_key] = institution_type_amount
        current_row += 1
        institution_type_null_amount, institution_type_null_items = get_invoice_items(
            parameters, start, end, Q(invoice__project_details__institution__institution_type__isnull=True)
        )
        summary.rows[current_row][summary_key] = institution_type_null_amount
        current_row += 1
    current_row += 1
    remote_amount, remote_items = get_invoice_items(parameters, start, end, Q(remote=True))
    summary.rows[current_row][summary_key] = remote_amount
    current_row += 1
    onsite_amount, onsite_items = get_invoice_items(parameters, start, end, Q(remote=False))
    summary.rows[current_row][summary_key] = onsite_amount


def get_invoice_items(
    params, start: datetime.datetime, end: datetime.datetime, extra_filter=None, total_include_discounts=True
) -> (Decimal, QuerySet[InvoiceDetailItem]):
    total_amount = Decimal(0)
    items = InvoiceDetailItem.objects.none()
    items_qs = InvoiceDetailItem.objects.filter(waived=False, invoice__voided_date__isnull=True)
    items_qs = items_qs.exclude(get_project_to_exclude_filter("invoice__project_details__"))
    if params.get_bool("tool_usage", "on"):
        tool_usages = items_qs.filter(
            end__date__gte=start, end__date__lte=end, item_type=BillableItemType.TOOL_USAGE.value
        ).annotate(
            remote=Case(
                When(
                    object_id__in=UsageEvent.objects.filter(pk=OuterRef("object_id"), remote_work=False).values_list(
                        "id", flat=True
                    ),
                    then=False,
                ),
                default=True,
                output_field=BooleanField(),
            )
        )
        if extra_filter:
            tool_usages = tool_usages.filter(extra_filter)
        total_amount += tool_usages.aggregate(Sum("amount"))["amount__sum"] or Decimal(0)
        if total_include_discounts:
            total_amount += tool_usages.aggregate(Sum("discount"))["discount__sum"] or Decimal(0)
        items = QuerySet.union(items, tool_usages)
    if params.get_bool("area_access", "on"):
        area_records = items_qs.filter(
            end__date__gte=start, end__date__lte=end, item_type=BillableItemType.AREA_ACCESS.value
        ).annotate(
            remote=Case(
                When(
                    item_type=BillableItemType.AREA_ACCESS.value,
                    object_id__in=AreaAccessRecord.objects.filter(
                        pk=OuterRef("object_id"), staff_charge__isnull=True
                    ).values_list("id", flat=True),
                    then=False,
                ),
                default=True,
                output_field=BooleanField(),
            )
        )
        if extra_filter:
            area_records = area_records.filter(extra_filter)
        total_amount += area_records.aggregate(Sum("amount"))["amount__sum"] or Decimal(0)
        if total_include_discounts:
            total_amount += area_records.aggregate(Sum("discount"))["discount__sum"] or Decimal(0)
        items = QuerySet.union(items, area_records)
    if params.get_bool("staff_charges", "on"):
        staff_work = items_qs.filter(
            end__date__gte=start, end__date__lte=end, item_type=BillableItemType.STAFF_CHARGE.value
        ).annotate(remote=Value(True, output_field=BooleanField()))
        if extra_filter:
            staff_work = staff_work.filter(extra_filter)
        total_amount += staff_work.aggregate(Sum("amount"))["amount__sum"] or Decimal(0)
        if total_include_discounts:
            total_amount += staff_work.aggregate(Sum("discount"))["discount__sum"] or Decimal(0)
        items = QuerySet.union(items, staff_work)
    if params.get_bool("consumables", "on"):
        consumables = items_qs.filter(
            end__date__gte=start, end__date__lte=end, item_type=BillableItemType.CONSUMABLE.value
        ).annotate(remote=Value(False, output_field=BooleanField()))
        if extra_filter:
            consumables = consumables.filter(extra_filter)
        total_amount += consumables.aggregate(Sum("amount"))["amount__sum"] or Decimal(0)
        if total_include_discounts:
            total_amount += consumables.aggregate(Sum("discount"))["discount__sum"] or Decimal(0)
        items = QuerySet.union(items, consumables)
    if params.get_bool("training", "on"):
        trainings = items_qs.filter(
            start__date__gte=start, start__date__lte=end, item_type=BillableItemType.TRAINING.value
        ).annotate(remote=Value(False, output_field=BooleanField()))
        if extra_filter:
            trainings = trainings.filter(extra_filter)
        total_amount += trainings.aggregate(Sum("amount"))["amount__sum"] or Decimal(0)
        if total_include_discounts:
            total_amount += trainings.aggregate(Sum("discount"))["discount__sum"] or Decimal(0)
        items = QuerySet.union(items, trainings)
    if params.get_bool("missed_reservations", "on"):
        reservations = items_qs.filter(
            end__date__gte=start, end__date__lte=end, item_type=BillableItemType.MISSED_RESERVATION.value
        ).annotate(remote=Value(False, output_field=BooleanField()))
        if extra_filter:
            reservations = reservations.filter(extra_filter)
        total_amount += reservations.aggregate(Sum("amount"))["amount__sum"] or Decimal(0)
        if total_include_discounts:
            total_amount += reservations.aggregate(Sum("discount"))["discount__sum"] or Decimal(0)
        items = QuerySet.union(items, reservations)
    if params.get_bool("custom_charges", "on"):
        custom_charges = items_qs.filter(
            end__date__gte=start, end__date__lte=end, item_type=BillableItemType.CUSTOM_CHARGE.value
        ).annotate(remote=Value(False, output_field=BooleanField()))
        if extra_filter:
            custom_charges = custom_charges.filter(extra_filter)
        total_amount += custom_charges.aggregate(Sum("amount"))["amount__sum"] or Decimal(0)
        if total_include_discounts:
            total_amount += custom_charges.aggregate(Sum("discount"))["discount__sum"] or Decimal(0)
        items = QuerySet.union(items, custom_charges)
    return total_amount, items
