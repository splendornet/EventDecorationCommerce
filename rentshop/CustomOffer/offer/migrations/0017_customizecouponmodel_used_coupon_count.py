# Generated by Django 2.0.2 on 2021-05-06 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0016_auto_20210429_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='customizecouponmodel',
            name='used_coupon_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
