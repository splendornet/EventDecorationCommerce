# Generated by Django 2.0.2 on 2021-01-14 17:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0045_auto_20210114_1719'),
        ('HeaderMenu', '0008_auto_20201107_1614'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExhibitionOffers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('category', models.ManyToManyField(to='catalogue.Category')),
                ('header_menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='HeaderMenu.Admin_Header')),
            ],
        ),
        migrations.CreateModel(
            name='ExhibitionOffersCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('manage_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manage_category', to='catalogue.Category')),
                ('manage_menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exhibition_menu', to='HeaderMenu.Manage_Menu')),
            ],
        ),
    ]
