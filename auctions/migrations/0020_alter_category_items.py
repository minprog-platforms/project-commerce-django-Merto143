# Generated by Django 4.1.3 on 2022-12-15 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0019_category_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='items',
            field=models.ManyToManyField(related_name='Cat_item', to='auctions.auction_item'),
        ),
    ]
