# Generated by Django 2.0.2 on 2020-03-04 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_productimage_img_sequence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='img_sequence',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
