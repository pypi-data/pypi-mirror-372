from django.db import models

from .. import model_settings


class AccountCodeMap(models.Model):
    entity_name = models.CharField(max_length=200)
    local_account_name = models.CharField(max_length=200)
    group_account_name = models.CharField(max_length=200)
    last_synced = models.DateTimeField(db_index=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "finance"
        default_permissions = ()
        db_table = 'finance"."account_code_map'


class GroupAccountCategory(models.Model):
    group_account_name = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    category1 = models.CharField(max_length=200)
    category2 = models.CharField(max_length=200)
    category3 = models.CharField(max_length=200)
    category4 = models.CharField(max_length=200)
    category5 = models.CharField(max_length=200)
    last_synced = models.DateTimeField(db_index=True)

    class Meta:
        managed = model_settings.DATAWAREHOUSE_MANAGED_MODELS
        app_label = "finance"
        default_permissions = ()
        db_table = 'finance"."group_account_category'
