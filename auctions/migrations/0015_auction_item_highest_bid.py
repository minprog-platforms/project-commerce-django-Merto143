# Generated by Django 4.1.3 on 2022-12-14 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_auction_item_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction_item',
            name='highest_bid',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
    ]