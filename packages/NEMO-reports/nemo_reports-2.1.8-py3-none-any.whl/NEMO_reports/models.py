from django.db import models

from NEMO_reports.views import reporting


class Report(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            (report["raw_permission"], f"Can view {report['report_title']}")
            for report in reporting.get_report_dict().values()
        ]
