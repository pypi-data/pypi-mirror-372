from datetime import timedelta
from django.utils import timezone
from core.choices import JobIntervalChoices
from netbox.jobs import JobRunner, system_job
from django.db.models import Q
from .. import models


@system_job(interval=JobIntervalChoices.INTERVAL_DAILY)
class HousekeepingJob(JobRunner):
    class Meta:
        name = "Sync Status Cleanup Job"

    def run(self, *args, **kwargs):
        batch_size = 1000
        while True:
            pks = models.SyncStatus.objects.filter(
                Q(is_latest=False)
                & Q(created__lt=timezone.now() - timedelta(days=90))
            ).values_list("pk", flat=True)[:batch_size]

            old_records = models.SyncStatus.objects.filter(pk__in=pks)
            if not old_records.exists():
                break

            old_records.delete()
