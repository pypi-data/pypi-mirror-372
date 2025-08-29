import decimal

from django.contrib.postgres.fields import ArrayField
from django.db import models

from .. import model_settings


class PaymentMethodSummary(models.Model):
    """Dump payment methods to the data warehouse."""

    last_synced = models.DateTimeField()
    customer_account_number = models.CharField(max_length=50)
    gocardless_id = models.CharField(max_length=100)
    stripe_id = models.CharField(max_length=100)
    description = models.CharField(max_length=250, blank=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_paymentmethod_summary'


class RevenueForecastSummary(models.Model):
    """Dump payment methods to the data warehouse."""

    last_synced = models.DateTimeField()
    month = models.DateField()
    total_contract_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_credit_value = models.DecimalField(max_digits=10, decimal_places=2)
    signed_value = models.DecimalField(max_digits=10, decimal_places=2)
    starting_value = models.DecimalField(max_digits=10, decimal_places=2)
    subs_total = models.IntegerField()
    subs_total_paying = models.IntegerField()
    subs_starting = models.IntegerField()
    subs_won = models.IntegerField()
    subs_lost = models.IntegerField()
    total_contract_paying_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
    )
    new_paying_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    upgrades_book = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    downgrades_book = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    upgrades_contract = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    downgrades_contract = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
    )
    loss_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_revenueforecast_summary'


class SubscriptionSummary(models.Model):
    """Dump data to the data warehouse so that it can be used by other reporting or internal tools like Vitally."""

    last_synced = models.DateTimeField()

    created = models.DateTimeField()
    updated = models.DateTimeField()
    salesperson = models.CharField(max_length=200)
    deal_originator = models.CharField(max_length=200, null=True)
    product = models.CharField(max_length=200, null=True)

    # customer details
    billing_entity_name = models.CharField(max_length=250)
    customer_name = models.CharField(max_length=200)
    # TODO rename to `customer_group_code` and `customer_account_code`
    customer_account_number = models.CharField(max_length=50, db_index=True)
    customer_group_code = models.CharField(max_length=50, db_index=True)
    # NOTE(William to Aidan): Are we sure this should be nullable?...we are storing nulls here for whatever reason.
    customer_xero_guid = models.UUIDField(blank=True, null=True)
    customer_primary_contact_name = models.CharField(max_length=200)
    customer_primary_contact_email = models.CharField(max_length=200)
    customer_accounts_contact_name = models.CharField(max_length=200)
    customer_accounts_contact_email = models.CharField(max_length=200)
    customer_address = models.CharField(max_length=1000)
    customer_company_tax_number = models.CharField(
        max_length=50, help_text="ABN, NZBN or VAT number."
    )

    # subscriptions
    subscription_guid = models.UUIDField()
    currency = models.CharField(max_length=3)
    signing_date = models.DateField()
    billing_date = models.DateField()

    plan = models.CharField(max_length=100)
    staff_addon_name = models.CharField(max_length=100)

    plan_included_licenses = models.IntegerField(blank=True, null=True)
    additional_committed_staff = models.IntegerField(blank=True, null=True)
    total_contracted_staff_licenses = models.IntegerField(blank=True, null=True)

    override_plan_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    override_staff_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    effective_discount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    total_contract_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    # addons
    hosting_addon_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    bi_addon_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    sla_addon_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    # workspaces
    workspaces = ArrayField(models.CharField(max_length=50), default=list, blank=True)

    # termination
    termination_date = models.DateField(blank=True, null=True)
    termination_code = models.TextField(blank=True)
    termination_reason = models.TextField(blank=True)
    primary_termination_reason = models.CharField(blank=True, max_length=25)
    termination_notification_date = models.DateField(blank=True, null=True)

    # current usage data
    current_expansion_chargeable = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    current_total_mrr_chargeable = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    current_total_used_staff_licenses = models.IntegerField(blank=True, null=True)
    current_total_additional_chargable_licenses = models.IntegerField(
        blank=True, null=True
    )
    current_monthly_recurring_credit = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    # last month usage data
    lastmonth_expansion_charged = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    lastmonth_total_mrr_charged = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    lastmonth_total_used_staff_licenses = models.IntegerField(blank=True, null=True)
    lastmonth_total_used_desk_licenses = models.IntegerField(blank=True, null=True)
    lastmonth_total_used_field_licenses = models.IntegerField(blank=True, null=True)
    lastmonth_total_additional_chargable_licenses = models.IntegerField(
        blank=True, null=True
    )

    # superseded data
    superseded_by_guid = models.UUIDField(blank=True, null=True)
    superseded_subscription_guid = models.UUIDField(blank=True, null=True)
    superseded_subscription_contract_value = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    superseded_subscription_upgrade_or_downgrade_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    # original subscription data
    original_signing_date = models.DateField(blank=True)
    original_billing_date = models.DateField(blank=True)
    original_plan = models.CharField(max_length=100, blank=True, null=True)
    original_total_contract_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    original_total_contracted_staff_licenses = models.IntegerField(
        blank=True, null=True
    )

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_subscription_summary'


class AddonSummary(models.Model):
    last_synced = models.DateTimeField()

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    equivalent = models.CharField(max_length=100, blank=True)
    metered_value = models.CharField(max_length=50)
    price_aud = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_nzd = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_gbp = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_cad = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_usd = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_eur = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    is_current = models.BooleanField(default=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_addon_summary'


class ProductAddonSummary(models.Model):
    last_synced = models.DateTimeField()

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, default="")
    billing_unit_description = models.CharField(max_length=100, blank=True, default="")
    is_usage_based = models.BooleanField(default=True)
    price_aud = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_nzd = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_gbp = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_cad = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_usd = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_eur = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    is_current = models.BooleanField(default=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."product_addon_summary'


class PlanSummary(models.Model):
    last_synced = models.DateTimeField()

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    equivalent = models.CharField(max_length=100, blank=True)
    included_users = models.IntegerField()
    price_aud = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_nzd = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_gbp = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_cad = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_usd = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_eur = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    recommended_addon_name = models.CharField(max_length=100, blank=True)

    is_current = models.BooleanField(default=True)
    expects_licensing_usage = models.BooleanField(default=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_plan_summary'


class RecurringCreditSummary(models.Model):
    """Dump data to the data warehouse so that it can be used by other reporting or internal tools like Vitally."""

    last_synced = models.DateTimeField()

    subscription_guid = models.UUIDField()
    customer_name = models.CharField(max_length=200)
    customer_account_number = models.CharField(max_length=50)
    currency = models.CharField(max_length=3)

    start_date = models.DateField()
    review_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_text = models.CharField(max_length=200)
    internal_note = models.CharField(max_length=500, blank=True)
    credit_classification = models.TextField()

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_recurring_credit_summary'


class ChangeSummary(models.Model):
    """Dump data to the data warehouse so that it can be used by other reporting or internal tools like Vitally."""

    last_synced = models.DateTimeField()

    subscription_guid = models.UUIDField()
    customer_name = models.CharField(max_length=200)
    customer_account_number = models.CharField(max_length=50)
    currency = models.CharField(max_length=3)

    change_type = models.TextField(null=True)
    date = models.DateField()
    note = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    salesperson = models.CharField(max_length=200)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_change_summary'


class ChargeSummary(models.Model):
    """Dump data to the data warehouse so that it can be used by other reporting or internal tools like Vitally."""

    last_synced = models.DateTimeField(null=True)  # Reflecting reality

    created = models.DateTimeField(null=True)  # Reflecting reality
    updated = models.DateTimeField(null=True)  # Reflecting reality
    requestor = models.CharField(max_length=200)

    subscription_guid = models.UUIDField()
    customer_name = models.CharField(max_length=200)
    customer_account_number = models.CharField(max_length=50)
    currency = models.CharField(max_length=3)

    itemcode = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
    account_code = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_category_1 = models.CharField(max_length=50)
    tracking_category_2 = models.CharField(max_length=50)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    invoice_date = models.DateField(null=True)
    invoice_reference = models.CharField(null=True, max_length=20)
    invoice_number = models.CharField(null=True, max_length=20)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_charge_summary'


class WorkspaceSummary(models.Model):
    """Dump data to the data warehouse so that any other tools can map workspaces back to customers and subscriptions."""

    last_synced = models.DateTimeField()

    guid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=50)
    customer_account_number = models.CharField(max_length=50)
    subscription_guid = models.UUIDField()
    timezone = models.CharField(max_length=50, default="")
    is_virtual_only = models.BooleanField(default=False)
    is_sandbox = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_workspace_summary'


class XeroContactSummary(models.Model):
    """Dump data to the data warehouse so that it can be used by other reporting or internal tools like Vitaly."""

    last_synced = models.DateTimeField()

    customer_name = models.CharField(max_length=200, null=True)
    customer_account_number = models.CharField(max_length=50, null=True)
    customer_first_name = models.CharField(max_length=100, null=True)
    customer_last_name = models.CharField(max_length=100, null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_xero_customer_summary'


class XeroInvoiceSummary(models.Model):
    """Dump data to the data warehouse so that it can be used by other reporting or internal tools like Vitaly."""

    last_synced = models.DateTimeField()

    invoice_guid = models.UUIDField()
    contact_guid = models.UUIDField()
    contact_name = models.CharField(max_length=200)
    contact_account_number = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    reference = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    status = models.CharField(max_length=50)
    currency = models.CharField(max_length=3)
    currency_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    is_sent = models.BooleanField(default=False, null=True)
    # TODO(@Aidan)... ?????
    repeating_invoice_guid = models.UUIDField(null=True)
    amount_due = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    fully_paid_on_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."billing_xero_invoice_summary'


class ConsolidatedProfitAndLossMonth(models.Model):
    """Each row is an account for a given month for an organisation, allowing us to do consolidated Profit & Loss."""

    last_synced = models.DateTimeField()
    entity_name = models.CharField(max_length=200)
    date = models.DateField()

    local_account_code = models.CharField(max_length=100)
    local_account_name = models.CharField(max_length=300)
    local_account_category = models.CharField(max_length=300)
    group_account_code = models.CharField(max_length=100)
    group_account_name = models.CharField(max_length=300)

    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    currency = models.CharField(max_length=3)

    reporting_fx_rate = models.DecimalField(
        max_digits=12, decimal_places=4, default=decimal.Decimal("0.0000")
    )
    reporting_subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    reporting_region = models.CharField(max_length=200)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."consolidated_profit_and_loss_month'


class NetPaidMRRValue(models.Model):
    """Each row is an account for a given month for an organisation, allowing us to do consolidated Profit & Loss."""

    last_synced = models.DateTimeField()
    entity_name = models.CharField(max_length=200)
    customer_account_code = models.CharField(max_length=200)
    date = models.DateField()

    local_account_code = models.CharField(max_length=100)
    local_account_name = models.CharField(max_length=300)

    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    currency = models.CharField(max_length=3)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"
        default_permissions = ()
        db_table = 'subscriptionmanager"."net_paid_mrr_value'


class RollForwardSummary(models.Model):
    last_synced = models.DateTimeField()
    month = models.DateField()
    customer_account_code = models.CharField(max_length=50)
    customer_group_code = models.CharField(max_length=50)
    billing_entity = models.CharField(max_length=250)
    subscription_guid = models.UUIDField()
    currency = models.CharField(max_length=3)
    won_mrr = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    contracted_mrr = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    user_expansion = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    user_expansion_mom = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    product_expansion = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    product_expansion_mom = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    pass_through = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    pass_through_mom = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    upgrade = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    downgrade = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    upgrade_or_downgrade = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    price_increase_upgrade = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    price_increase_downgrade = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    churn_from_live = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    churn_from_not_live = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    billable_mrr = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    mmr_transfered = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    contracted_discount_mrr = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    delayed_onboarding_mrr = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    other_credit_mrr = models.DecimalField(
        max_digits=10, decimal_places=2, default=decimal.Decimal("0.00")
    )
    note = models.TextField(blank=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"
        default_permissions = ()
        db_table = 'subscriptionmanager"."roll_forward_summary'


class Workspace(models.Model):
    name = models.CharField(unique=True, max_length=30)
    customer = models.CharField(max_length=30)
    cluster = models.CharField()
    account_number = models.CharField(max_length=25, null=True)
    tags = ArrayField(
        models.CharField(),
        default=list,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "customer": self.customer,
            "cluster": self.cluster,
            "account_number": self.account_number,
            "tags": self.tags,
        }

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"

        default_permissions = ()
        db_table = 'subscriptionmanager"."workspace'

        indexes = [
            models.Index(
                fields=["cluster"],
            )
        ]


class FixedFXRate(models.Model):
    currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    applicable_from = models.DateField(blank=True, null=True)
    applicable_to = models.DateField(blank=True, null=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"
        default_permissions = ()
        db_table = 'subscriptionmanager"."fixed_fx_rate'


class InvoiceLineItemSummary(models.Model):
    """
    Sync future invoice line items to the data warehouse.
    Useful for expansion calculations
    """

    last_synced = models.DateTimeField(null=True)

    customer_account_number = models.CharField(max_length=25)

    account_code = models.CharField(max_length=20)
    key = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=3)

    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        blank=True, null=True, max_digits=5, decimal_places=2
    )
    tax_rate = models.CharField(max_length=20)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "subscriptionmanager"
        default_permissions = ()
        db_table = 'subscriptionmanager"."invoice_line_item_summary'
