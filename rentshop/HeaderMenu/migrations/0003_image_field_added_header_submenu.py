# Generated by Django 2.0.2 on 2019-02-19 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HeaderMenu', '0002_admin_header_sequence_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin_headersubmenu',
            name='menu_image',
            field=models.ImageField(blank=True, default='media/image_not_found.jpg', max_length=255, null=True, upload_to='header_menu/'),
        ),
    ]
