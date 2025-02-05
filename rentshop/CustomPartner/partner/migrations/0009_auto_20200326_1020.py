# Generated by Django 2.0.2 on 2020-03-26 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0008_stockrecord_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockrecord',
            name='rent_price_with_tax',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='stockrecord',
            name='sale_price_with_tax',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
