# Generated by Django 4.1.3 on 2022-12-13 19:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_rename_atchlist_auction_item_watchlist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction_item',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Auction_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='auction_item',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='Watch_item', to=settings.AUTH_USER_MODEL),
        ),
    ]
