# Generated by Django 2.0.6 on 2018-07-23 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_product_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_approved',
            field=models.CharField(default='Pending', max_length=30),
        ),
    ]
