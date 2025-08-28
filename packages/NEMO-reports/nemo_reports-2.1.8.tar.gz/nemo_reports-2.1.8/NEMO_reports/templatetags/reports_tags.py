from NEMO.models import User
from django import template

register = template.Library()


@register.filter
def has_any_report_permissions(user: User):
    from NEMO_reports.views.reporting import get_report_dict

    return any([user.has_perm(report["permission"]) for report in get_report_dict().values()])
