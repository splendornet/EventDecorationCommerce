# Generated by Django 2.0.6 on 2018-07-16 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SliderImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slider_image', models.ImageField(upload_to='slider')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
