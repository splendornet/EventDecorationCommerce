# Generated by Django 2.0.2 on 2021-01-15 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0016_auto_20210104_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockrecord',
            name='sale_tax_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
