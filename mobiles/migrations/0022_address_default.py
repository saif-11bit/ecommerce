# Generated by Django 3.0.6 on 2020-06-28 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0021_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]
