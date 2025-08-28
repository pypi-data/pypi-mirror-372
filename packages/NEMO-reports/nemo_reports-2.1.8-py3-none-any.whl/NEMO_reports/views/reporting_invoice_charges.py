import datetime
from _decimal import Decimal

from NEMO.models import AccountType, ProjectDiscipline, ProjectType
from NEMO.views.customization import ProjectsAccountsCustomization
from NEMO_billing.invoices.models import Invoice, InvoiceSummaryItem
from NEMO_billing.models import CoreFacility, Institution, InstitutionType
from NEMO_billing.rates.models import RateCategory
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Case, OuterRef, QuerySet, Subquery, Sum, When
from django.db.models.functions import Coalesce
from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET

from NEMO_reports.views.reporting import (
    DataDisplayTable,
    ReportingParameters,
    SummaryDisplayTable,
    get_month_range,
    get_monthly_rule,
    get_project_to_exclude_filter,
    get_report_dict,
    report_export,
    reporting_dictionary,
)


@login_required
@permission_required(get_report_dict()["invoice_charges"]["permission"])
@require_GET
def invoice_charges(request):
    params = ReportingParameters(request)
    data = DataDisplayTable()
    summary = SummaryDisplayTable()

    if not params.errors:
        split_by_month = params.get_bool("split_by_month")
        cumulative_count = params.get_bool("cumulative_count")
        # Split since invoices are by month, any day in that month counts as the full month
        start, end = params.start, params.end
        start, start_month_end = get_month_range(start)
        end_month_start, end = get_month_range(end)
        monthly_start = None
        if cumulative_count:
            split_by_month = True
            monthly_start, monthly_end = get_month_range(start)

        if params.get_bool("detailed_data"):
            data.headers = [
                ("invoice_number", "Invoice"),
                ("invoice_project", "Project"),
                (
                    "invoice_project_identifier",
                    ProjectsAccountsCustomization.get("project_application_identifier_name"),
                ),
            ]
            if ProjectType.objects.exists():
                project_type_label = (
                    "Project types"
                    if ProjectsAccountsCustomization.get_bool("project_type_allow_multiple")
                    else "Project type"
                )
                data.add_header(("invoice_project_types", project_type_label))
            data.headers += [
                (
                    "invoice_project_identifier",
                    ProjectsAccountsCustomization.get("project_application_identifier_name"),
                ),
                ("invoice_date", "Date"),
                ("invoice_tax", "Tax"),
                ("invoice_total", "Amount (tax incl.)"),
            ]

            if CoreFacility.objects.exists():
                data.add_header(("core_facility", "Core Facility"))
            if ProjectDiscipline.objects.exists():
                data.add_header(("discipline", "Discipline"))
            if AccountType.objects.exists():
                data.add_header(("account_type", "Account type(s)"))
            if RateCategory.objects.exists():
                data.add_header(("rate_category", "Rate category"))
            if Institution.objects.exists():
                data.add_header(("institution_name", "Institution Name"))
                data.add_header(("institution_type", "Institution Type"))

            total_data_qs = get_invoice_query_set(start, end)
            for invoice in total_data_qs:
                invoice: Invoice = invoice
                project_details = invoice.project_details
                project_types = project_details.project.project_types.all()
                discipline = project_details.project.discipline
                account_type = project_details.project.account.type
                institution = project_details.institution
                institution_type = institution.institution_type if institution else None

                data_row = {
                    "invoice_number": invoice.invoice_number,
                    "invoice_project": invoice.project_details.name,
                    "invoice_project_types": ", ".join([project_type.name for project_type in project_types]),
                    "invoice_project_identifier": invoice.project_details.project.application_identifier,
                    "invoice_date": invoice.start.strftime("%B %Y"),
                    "invoice_total": invoice.total_amount,
                    "invoice_tax": invoice_tax(invoice),
                    "core_facility": ", ".join(
                        [
                            core_facility or "General charges"
                            for core_facility in set(
                                invoice.invoicesummaryitem_set.values_list("core_facility", flat=True)
                            )
                        ]
                    ),
                    "discipline": discipline.name if discipline else "N/A",
                    "account_type": account_type.name if account_type else "N/A",
                    "rate_category": (
                        invoice.project_details.category.name if invoice.project_details.category else "N/A"
                    ),
                    "institution_name": institution.name if institution else "N/A",
                    "institution_type": institution_type.name if institution_type else "N/A",
                }
                data.add_row(data_row)
            data.rows.sort(key=lambda x: x["invoice_number"], reverse=True)

        summary.add_header(("item", "Item"))
        summary.add_row({"item": "Total amount"})
        if CoreFacility.objects.exists():
            summary.add_row({"item": "By core facility"})
            for core_facility in CoreFacility.objects.all():
                summary.add_row({"item": f"{core_facility.name}"})
            summary.add_row({"item": "N/A"})
            summary.add_row({"item": "Taxes"})
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
        if RateCategory.objects.exists():
            summary.add_row({"item": "By project rate category"})
            for category in RateCategory.objects.all():
                summary.add_row({"item": f"{category.name}"})
        if InstitutionType.objects.exists():
            summary.add_row({"item": "By institution type"})
            for institution_type in InstitutionType.objects.all():
                summary.add_row({"item": f"{institution_type.name}"})
            summary.add_row({"item": "N/A"})
        # summary.add_row({"item": "By remote status"})
        # summary.add_row({"item": "Remote"})
        # summary.add_row({"item": "On-site"})

        if split_by_month:
            # Create new start/end of month dates
            for month in get_monthly_rule(start, end):
                month_key = f"month_{month.strftime('%Y')}_{month.strftime('%m')}"
                summary.add_header((month_key, month.strftime("%b %Y")))
                month_start, month_end = get_month_range(month)
                add_summary_info(request, summary, monthly_start or month_start, month_end, month_key)
        else:
            summary.add_header(("value", "Value"))
            add_summary_info(request, summary, start, end)

        if params.get_bool("export"):
            return report_export([summary, data], "invoice_charges", start, end)

    dictionary = {
        "data": data,
        "summary": summary,
        "errors": params.errors,
    }

    return render(request, "NEMO_reports/report_base.html", reporting_dictionary("invoice_charges", params, dictionary))


def add_summary_info(request: HttpRequest, summary: SummaryDisplayTable, start, end, summary_key=None):
    summary_key = summary_key or "value"
    monthly_invoices = get_invoice_query_set(start, end)
    summary.rows[0][summary_key] = monthly_invoices.aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
    current_row = 1
    if CoreFacility.objects.exists():
        for facility in CoreFacility.objects.all():
            current_row += 1
            sub = InvoiceSummaryItem.objects.filter(
                invoice=OuterRef("pk"),
                core_facility=facility.name,
                summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL,
            ).values("amount")
            facility_invoices = monthly_invoices.annotate(**{f"facility_total_{facility.id}": Subquery(sub)})
            summary.rows[current_row][summary_key] = facility_invoices.aggregate(Sum(f"facility_total_{facility.id}"))[
                f"facility_total_{facility.id}__sum"
            ] or Decimal(0)
        # Add general (None) subtotal too
        current_row += 1
        sub = InvoiceSummaryItem.objects.filter(
            invoice=OuterRef("pk"),
            core_facility=None,
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL,
        ).values("amount")
        general_invoices = monthly_invoices.annotate(facility_total_general=Subquery(sub))
        summary.rows[current_row][summary_key] = general_invoices.aggregate(Sum("facility_total_general"))[
            "facility_total_general__sum"
        ] or Decimal(0)
        # Add taxes subtotal too
        current_row += 1
        sub = InvoiceSummaryItem.objects.filter(
            invoice=OuterRef("pk"), summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX
        ).values("amount")
        tax_invoices = monthly_invoices.annotate(tax_amount=Subquery(sub))
        summary.rows[current_row][summary_key] = tax_invoices.aggregate(Sum("tax_amount"))[
            "tax_amount__sum"
        ] or Decimal(0)
        current_row += 1  # For mid table header
    if ProjectType.objects.exists():
        for project_type in ProjectType.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = monthly_invoices.filter(
                project_details__project__project_types__in=[project_type]
            ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1
        summary.rows[current_row][summary_key] = monthly_invoices.filter(
            project_details__project__project_types__isnull=True
        ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1  # For mid table header
    if ProjectDiscipline.objects.exists():
        for discipline in ProjectDiscipline.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = monthly_invoices.filter(
                project_details__project__discipline=discipline
            ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1
        summary.rows[current_row][summary_key] = monthly_invoices.filter(
            project_details__project__discipline__isnull=True
        ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1  # For mid table header
    if AccountType.objects.exists():
        for account_type in AccountType.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = monthly_invoices.filter(
                project_details__project__account__type=account_type
            ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1
        summary.rows[current_row][summary_key] = monthly_invoices.filter(
            project_details__project__account__type__isnull=True
        ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1  # For mid table header
    if RateCategory.objects.exists():
        for category in RateCategory.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = monthly_invoices.filter(
                project_details__category=category
            ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1  # For mid table header
    if InstitutionType.objects.exists():
        for institution_type in InstitutionType.objects.all():
            current_row += 1
            summary.rows[current_row][summary_key] = monthly_invoices.filter(
                project_details__institution__institution_type=institution_type
            ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1
        summary.rows[current_row][summary_key] = monthly_invoices.filter(
            project_details__institution__institution_type__isnull=True
        ).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal(0)
        current_row += 1
    current_row += 1
    # params = ReportingParameters(request)
    # remote_amount, remote_items = get_invoice_items(params, start, end, Q(remote=True))
    # summary.rows[current_row][summary_key] = remote_amount
    # current_row += 1
    # onsite_amount, onsite_items = get_invoice_items(params, start, end, Q(remote=False))
    # summary.rows[current_row][summary_key] = onsite_amount


def get_invoice_query_set(start: datetime.datetime, end: datetime.datetime) -> QuerySet[Invoice]:
    query = Invoice.objects.filter(voided_date__isnull=True, start__gte=start, start__lte=end)
    query = query.exclude(get_project_to_exclude_filter("project_details__"))
    return query


def invoice_tax(invoice) -> Decimal:
    return invoice.invoicesummaryitem_set.aggregate(
        total_tax=Coalesce(
            Sum(
                Case(
                    When(summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX, then="amount"),
                    default=Decimal(0),
                )
            ),
            Decimal(0),
        )
    )["total_tax"]
