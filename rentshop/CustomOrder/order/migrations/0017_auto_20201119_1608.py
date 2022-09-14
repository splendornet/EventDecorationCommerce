# Generated by Django 2.0.2 on 2020-11-19 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0016_auto_20201112_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='advance_payment_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='balance_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
