# Generated by Django 2.0.2 on 2020-12-03 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0032_auto_20201126_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxation',
            name='apply_to',
            field=models.CharField(choices=[('1', 'For all rental products'), ('2', 'For all selling products'), ('3', 'For few products'), ('4', 'For all professional products')], max_length=255),
        ),
    ]
