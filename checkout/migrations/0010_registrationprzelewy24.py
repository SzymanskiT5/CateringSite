# Generated by Django 3.2.4 on 2021-07-13 16:03

from django.db import migrations, models
import django.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0009_delete_purchaserinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationPrzelewy24',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posID', models.IntegerField(default=11111)),
                ('sessionId', models.CharField(default='test7', max_length=100)),
                ('currency', models.CharField(default='PLN', max_length=3)),
                ('description', models.CharField(default='test order', max_length=1024)),
                ('email', models.EmailField(default='john.doe@example.com', max_length=50)),
                ('address', models.CharField(max_length=80, null=True)),
                ('city', models.CharField(max_length=50, null=True)),
                ('country', models.CharField(default='PL', max_length=2)),
                ('phone', models.CharField(max_length=12, null=True)),
                ('language', models.CharField(default='pl', max_length=2)),
                ('method', models.IntegerField(null=True)),
                ('urlReturn', models.URLField(default='http://127.0.0.1:8000/cart')),
                ('channel', models.IntegerField(default=16, null=True)),
                ('waitForResult', models.BooleanField(null=True)),
                ('regulationAccept', models.BooleanField(default=False)),
                ('shipping', models.IntegerField(null=True, verbose_name=django.db.models.fields.IntegerField)),
                ('transferLabel', models.CharField(max_length=20, null=True)),
                ('mobileLib', models.IntegerField(default=1, null=True)),
                ('sdkVersion', models.CharField(max_length=10, null=True)),
                ('sign', models.CharField(default='596af9bc39271b4cfdab45937', max_length=100)),
                ('encoding', models.CharField(max_length=15, null=True)),
                ('methodRefId', models.CharField(max_length=250)),
            ],
        ),
    ]