# Generated by Django 2.0.2 on 2021-04-14 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0057_product_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_package',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='product_package',
            field=models.ManyToManyField(blank=True, related_name='_product_product_package_+', to='catalogue.Product'),
        ),
    ]
