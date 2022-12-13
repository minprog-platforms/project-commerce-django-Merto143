# Generated by Django 4.1.3 on 2022-12-13 15:14

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_watchlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction_item',
            name='owner',
        ),
        migrations.AddField(
            model_name='auction_item',
            name='atchlist',
            field=models.ManyToManyField(blank=True, related_name='Auction_item', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Watchlist',
        ),
    ]
