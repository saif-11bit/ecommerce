# Generated by Django 3.0.6 on 2020-06-23 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0015_auto_20200623_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponcode',
            name='amount',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
    ]
