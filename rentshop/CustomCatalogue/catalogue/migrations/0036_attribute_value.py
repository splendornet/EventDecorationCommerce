# Generated by Django 2.0.2 on 2020-12-15 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0035_product_product_margin'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='value',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
