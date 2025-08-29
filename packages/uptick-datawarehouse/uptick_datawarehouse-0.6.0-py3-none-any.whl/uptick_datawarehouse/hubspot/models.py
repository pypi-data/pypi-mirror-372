from django.contrib.postgres.fields import ArrayField
from django.db import models


class CustomerContacts(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=200)
    tenant = models.CharField(db_index=True, max_length=200)
    license = models.CharField(max_length=10, db_index=True)
    groups = ArrayField(models.CharField(max_length=150), default=list, blank=True)
    currency = models.CharField(max_length=3)

    class Meta:
        # Created via a view
        managed = False
        app_label = "hubspot"
        default_permissions = ()
        db_table = 'hubspot"."customer_contacts'
