# Generated by Django 2.0.2 on 2020-12-04 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0019_line_product_attributes'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='customized_order',
            field=models.BooleanField(default=False),
        ),
    ]
