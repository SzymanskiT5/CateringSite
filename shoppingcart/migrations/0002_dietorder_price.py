# Generated by Django 3.2.4 on 2021-06-14 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingcart', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dietorder',
            name='price',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]