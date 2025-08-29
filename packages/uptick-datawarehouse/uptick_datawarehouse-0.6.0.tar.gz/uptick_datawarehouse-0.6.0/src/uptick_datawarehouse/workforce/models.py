from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection, models

from .. import model_settings


class WorkforceAddressSummary(models.Model):
    class Countries(models.TextChoices):
        AU = "AU", "Australia"
        NZ = "NZ", "New Zealand"

    tenant = models.CharField(db_index=True, max_length=200)
    last_synced = models.DateTimeField(null=True)
    prop_status = models.CharField(max_length=30, blank=True)
    prop_id = models.IntegerField()
    prop_created = models.DateTimeField(null=True)
    address = models.CharField(
        max_length=1000,
        blank=True,
        help_text="Exact and validated registered postal address.",
    )
    display = models.TextField(
        max_length=1000,
        blank=False,
        help_text="Address that will be used for display purposes.",
    )
    country = models.CharField(
        max_length=2, blank=True, default="AU", choices=Countries.choices
    )
    gnaf_id = models.CharField(max_length=30, default="", blank=True)
    state = models.CharField(
        max_length=50, blank=True, default="", verbose_name="State or Region"
    )
    postal_code = models.CharField(
        max_length=15, blank=True, default="", verbose_name="Postal or Zip code"
    )
    coords = models.CharField(max_length=40, blank=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."address_summary'


class ConstanceSetting(models.Model):
    slug = models.CharField(max_length=100)
    setting_name = models.TextField()
    setting_value = models.TextField(null=True)
    last_synced = models.DateTimeField(null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."constance_summary'


class ExtensionSummary(models.Model):
    tenant = models.CharField(db_index=True, max_length=200)
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(db_index=True)
    last_synced = models.DateTimeField(null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."extension_summary'


class FeatureFlagSummary(models.Model):
    tenant = models.CharField(db_index=True, max_length=200)
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(db_index=True)
    last_synced = models.DateTimeField(null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."featureflag_summary'


class UserSummaryRow(models.Model):
    last_synced = models.DateTimeField(db_index=True)
    tenant = models.CharField(db_index=True, max_length=200)
    user_pk = models.PositiveIntegerField(db_index=True)
    email = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255)
    license = models.CharField(max_length=10, db_index=True)
    is_active = models.BooleanField(db_index=True)
    is_superuser = models.BooleanField(db_index=True)
    created = models.DateTimeField(db_index=True)
    last_access = models.DateTimeField(null=True, blank=True, db_index=True)
    groups = ArrayField(models.CharField(max_length=150), default=list, blank=True)
    addons = ArrayField(models.CharField(max_length=150), default=list, blank=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."customer_all_users'


class CustomReportSummary(models.Model):
    """Custom reports are collected to support running regression tests."""

    tenant = models.CharField(db_index=True, max_length=200)
    last_synced = models.DateTimeField(db_index=True)
    custom_report_pk = models.PositiveIntegerField(db_index=True)
    query = models.TextField()

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."customer_custom_reports'


class UsageMetrics(models.Model):
    tenant = models.CharField(db_index=True, max_length=200)
    count_name = models.CharField(db_index=True, max_length=200)
    stat_count = models.BigIntegerField()
    for_date = models.DateField(db_index=True)
    as_of = models.DateTimeField(db_index=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        db_table = 'workforce"."usage_metrics'
        indexes = [
            models.Index(
                fields=["tenant", "count_name", "-as_of"],
                name="usage_metrics_latest_btree",
            ),
            models.Index(
                fields=["tenant", "count_name", "-for_date"],
                name="usage_metrics_date_btree",
            ),
        ]


class ServerUsageData(models.Model):
    workspace = models.CharField(max_length=50, db_index=True)
    for_date = models.DateField(db_index=True)
    as_of = models.DateTimeField()
    usage_key = models.CharField(max_length=100, db_index=True)
    amount = models.IntegerField(default=0)

    # Not sure this'll be used, but here just in case
    data = models.JSONField(blank=True, null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."server_usage_data'
        unique_together = ("workspace", "for_date", "usage_key")


class ServerUsage(models.Model):
    """Mechanism for this Workspace to update the datawarehouse with it's resource utilisation for licensing."""

    tenant = models.CharField(max_length=200, db_index=True)
    staff_licenses_total = models.IntegerField()
    staff_licenses_used = models.IntegerField()
    staff_licenses_additional = models.IntegerField()
    desk_licenses_used = models.IntegerField()
    field_licenses_used = models.IntegerField()
    contractor_licenses_used = models.IntegerField()
    customer_licenses_used = models.IntegerField()
    api_licenses_used = models.IntegerField()
    reporting_licenses_used = models.IntegerField()
    timesheet_licenses_used = models.IntegerField()
    contractor_addons_used = models.IntegerField(default=0)
    sms_notifications = models.IntegerField(default=0)
    premium_portal_tenancies = models.IntegerField(default=0)
    premium_portal_buildings = models.IntegerField(default=0)
    last_synced = models.DateTimeField()
    for_date = models.DateField(db_index=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."licensing_usage'
        unique_together = ("tenant", "for_date")


class TemplateStatSummary(models.Model):
    last_synced = models.DateTimeField(db_index=True)
    tenant = models.CharField(db_index=True, max_length=200)
    object_pk = models.IntegerField()
    object_content_type_name = models.CharField(max_length=100)
    created = models.DateTimeField()
    region = models.CharField(max_length=10)
    name = models.CharField(max_length=250)
    key = models.CharField(max_length=250)
    extends = models.CharField(max_length=250, blank=True, default="")
    usage_total = models.IntegerField()
    usage_this_year = models.IntegerField()
    usage_last_year = models.IntegerField()
    libraries_loaded = ArrayField(
        models.CharField(max_length=250), default=list, blank=True
    )
    deprecated_functions = ArrayField(
        models.CharField(max_length=250), default=list, blank=True
    )
    is_active = models.BooleanField()

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        db_table = 'workforce"."template_stat_summary'


class SyncedData(models.Model):
    """Upsert entire json payloads into the datawarehouse.

    The purpose is store arbitrary blob payloads (not individual models but json tabular data of low rows)

    Example usecases:
    - all templates
    - all postgres tables and their metrics
    """

    tenant = models.CharField(max_length=200, db_index=True)
    key = models.CharField(max_length=200, db_index=True)
    data = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    last_synced = models.DateTimeField(db_index=True, null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."synced_data'
        unique_together = ("tenant", "key")


class Benchmark(models.Model):
    count_name = models.CharField(max_length=200)
    country_cohort = models.CharField(max_length=200)
    size_cohort = models.CharField(max_length=20)
    industry_cohort = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    tenant_count = models.IntegerField()

    @classmethod
    def refresh_view(cls, concurrent: bool = True) -> None:
        query = f"refresh materialized view {"concurrently " if concurrent else ""} workforce.usage_metrics_benchmarks;"
        with connection.cursor() as cursor:
            cursor.execute(query)

    class Meta:
        # Created via a materialized view
        managed = False
        app_label = "workforce"
        default_permissions = ()
        db_table = 'workforce"."usage_metrics_benchmarks'


class LatestUsageMetrics(models.Model):
    """Gets the latest callhome value for each stat, month and workspace"""

    # -- --- Used by: Equals for usage analysis
    workspace = models.CharField(max_length=200)  # was tenant
    account_number = models.CharField(max_length=50)  # was customer_account_number
    subscription_currency = models.CharField(max_length=3)  # was currency
    month_start = models.DateField()
    dimension = models.CharField(max_length=200)  # Was count_name
    value = models.BigIntegerField()  # Was stat_count
    as_of = models.DateTimeField()  # Was as_of

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "workforce"
        db_table = 'workforce"."mv_usage_metrics_latest'

        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "dimension", "month_start"],
                name="idx_mvusagemetricslatest",
            )
        ]
