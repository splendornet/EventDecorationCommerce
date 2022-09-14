# Generated by Django 2.0.2 on 2021-06-08 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0020_auto_20210607_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricerangemodel',
            name='price_rng',
            field=models.CharField(choices=[('1-1999', 'Below 1,999'), ('2000-4999', '2,000 - 4,999'), ('5000-6999', '5,000 - 6,999'), ('7000-9999', '7,000 - 9,999'), ('10000-24999', '10,000 - 24,999'), ('25000-1000000', 'Above 25,000'), ('15000-49999', '15,000 - 49,999'), ('20000-49999', '20,000 - 49,999'), ('30000-69999', '30,000 - 69,999'), ('50000-74999', '50,000 - 74,999'), ('50000-79999', '50,000 - 79,999'), ('70000-99999', '70,000 - 99,999'), ('75000-99999', '75,000 - 99,999'), ('80000-99999', '80,000 - 99,999'), ('100000-149999', '1,00,000 - 1,49,999'), ('150000-199999', '1,50,000 - 1,99,999'), ('200000-1000000', '2,00,000 Onwards')], max_length=25),
        ),
    ]
