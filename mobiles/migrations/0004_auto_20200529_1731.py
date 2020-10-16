# Generated by Django 3.0.6 on 2020-05-29 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0003_item_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('S', 'Shirt'), ('SW', 'Sport wear'), ('OW', 'Outwear')], max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], max_length=300, null=True),
        ),
    ]