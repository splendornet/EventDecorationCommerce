# Generated by Django 2.0.2 on 2020-11-06 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0023_comboproductsmaster_max_allowed'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='daily_capacity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
