# Generated by Django 2.0.2 on 2020-12-17 17:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0036_attribute_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute_mapping',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_mapping', to='catalogue.Product'),
        ),
    ]
