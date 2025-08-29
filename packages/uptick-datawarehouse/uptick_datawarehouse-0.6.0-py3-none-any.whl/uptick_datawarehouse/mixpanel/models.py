# Create your models here.

from django.db import models

from .. import model_settings


class MixpanelUserCohort(models.Model):
    """Mixpanel user cohort information per user row"""

    last_synced = models.DateTimeField(auto_now_add=True)
    user_slug = models.TextField(
        db_index=True, help_text="User's unique identifier eg: arafire_321"
    )
    # Editable name of the cohort
    cohort_name = models.CharField(
        max_length=150, db_index=True, help_text="Cohort name from Mixpanel", default=""
    )
    # This is stored as a string because mixpanel cohort_id is a string
    cohort_id = models.TextField(
        db_index=True, help_text="Cohort ID from Mixpanel", default=""
    )

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "mixpanel"

        default_permissions = ()
        db_table = 'mixpanel"."mixpanel_user_cohort'
        unique_together = ("user_slug", "cohort_id")
