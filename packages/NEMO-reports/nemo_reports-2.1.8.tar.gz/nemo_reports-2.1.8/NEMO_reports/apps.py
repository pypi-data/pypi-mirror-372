from django.apps import AppConfig
from django.conf import settings

from . import app_settings as defaults

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class NemoReportsConfig(AppConfig):
    name = "NEMO_reports"
    verbose_name = "NEMO Reports"

    def ready(self):
        from NEMO.plugins.utils import check_extra_dependencies

        """
        This code will be run when Django starts.
        """
        check_extra_dependencies(self.name, ["NEMO", "NEMO-CE"])
