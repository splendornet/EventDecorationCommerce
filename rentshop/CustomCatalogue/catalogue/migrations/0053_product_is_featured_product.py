# Generated by Django 2.0.2 on 2021-02-23 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0052_auto_20210223_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_featured_product',
            field=models.BooleanField(default=False),
        ),
    ]
