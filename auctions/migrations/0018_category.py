# Generated by Django 4.1.3 on 2022-12-15 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_alter_bid_bid_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('Fashion', 'Fashion'), ('Furniture', 'Furniture'), ('Other', 'Other')], max_length=50)),
            ],
        ),
    ]
