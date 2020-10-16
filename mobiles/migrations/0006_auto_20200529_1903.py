# Generated by Django 3.0.6 on 2020-05-29 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0005_item_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='discount_price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.FloatField(),
        ),
    ]
