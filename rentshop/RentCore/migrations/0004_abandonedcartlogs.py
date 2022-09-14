# Generated by Django 2.0.2 on 2021-01-05 14:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wishlists', '0002_auto_20160111_1108'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('basket', '0007_basket_customized_basket'),
        ('RentCore', '0003_customflatpages_page_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbandonedCartLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('cart', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ab_cart', to='basket.Basket')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ab_cart_users', to=settings.AUTH_USER_MODEL)),
                ('wishlist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ab_wish_list', to='wishlists.WishList')),
            ],
        ),
    ]
