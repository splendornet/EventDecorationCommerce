# Generated by Django 2.0.2 on 2020-03-16 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_auto_20200304_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='is_dp_image',
            field=models.BooleanField(default=False),
        ),
    ]
