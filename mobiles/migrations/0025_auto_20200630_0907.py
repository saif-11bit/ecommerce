# Generated by Django 3.0.6 on 2020-06-30 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0024_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='one_click_purchasing',
            field=models.BooleanField(default=False),
        ),
    ]
