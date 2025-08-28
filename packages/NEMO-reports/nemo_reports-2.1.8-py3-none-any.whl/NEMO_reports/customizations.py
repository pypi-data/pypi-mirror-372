from typing import Dict

from NEMO.decorators import customization
from NEMO.exceptions import InvalidCustomizationException
from NEMO.models import Project
from NEMO.views.customization import CustomizationBase
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list


@customization(title="Reports", key="reports")
class ReportsCustomization(CustomizationBase):
    variables = {
        "reports_first_day_of_week": "1",
        "reports_default_daterange": "",
        "reports_exclude_projects": "",
        "reports_exclude_no_charge_projects": "",
        "reports_timedelta_format": "{D}d {H}h {M}m {S:.0f}s",
    }

    def context(self) -> Dict:
        # Override to add list of tools
        dictionary = super().context()
        dictionary["projects"] = Project.objects.all()
        dictionary["selected_projects"] = Project.objects.filter(id__in=self.get_list_int("reports_exclude_projects"))
        return dictionary

    def validate(self, name, value):
        if name == "reports_exclude_projects" and value:
            validate_comma_separated_integer_list(value)

    def save(self, request, element=None) -> Dict[str, Dict[str, str]]:
        errors = super().save(request, element)
        exclude_projects = ",".join(request.POST.getlist("reports_exclude_projects_list", []))
        try:
            self.validate("reports_exclude_projects", exclude_projects)
            type(self).set("reports_exclude_projects", exclude_projects)
        except (ValidationError, InvalidCustomizationException) as e:
            errors["reports_exclude_projects"] = {"error": str(e.message or e.msg), "value": exclude_projects}
        return errors
