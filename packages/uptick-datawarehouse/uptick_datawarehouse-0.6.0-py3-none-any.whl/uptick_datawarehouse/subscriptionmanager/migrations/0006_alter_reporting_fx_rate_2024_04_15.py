from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptionmanager", "0005_consolidatedprofitandlossmonth"),
    ]

    operations = [
        migrations.AlterField(
            model_name="consolidatedprofitandlossmonth",
            name="reporting_fx_rate",
            field=models.DecimalField(
                decimal_places=4, default=Decimal("0.0000"), max_digits=12
            ),
        ),
    ]
