# Generated by Django 2.0.2 on 2020-11-26 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0029_attribute_attribute_mapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_cost_type',
            field=models.CharField(choices=[('Single', 'Single'), ('Multiple', 'Multiple')], default='Single', max_length=255),
        ),
    ]
