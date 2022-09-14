# Generated by Django 2.0.2 on 2021-01-14 18:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('HeaderMenu', '0009_exhibitionoffers_exhibitionofferscategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exhibitionofferscategory',
            name='manage_menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exhibition_menu', to='HeaderMenu.ExhibitionOffers'),
        ),
    ]
