# Generated by Django 2.0.2 on 2020-11-07 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0024_product_daily_capacity'),
        ('HeaderMenu', '0006_manage_menu'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManageMenuMasterProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('manage_menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manage_menu', to='HeaderMenu.Manage_Menu')),
                ('manage_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manage_product', to='catalogue.Product')),
            ],
        ),
    ]
