# Generated by Django 4.1.3 on 2022-12-14 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_rename_comment_comment_comment_input'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment_input',
            field=models.TextField(max_length=250),
        ),
    ]
