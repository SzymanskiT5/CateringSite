# Generated by Django 3.2.4 on 2021-06-30 13:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menu', '0003_diet_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surname', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=20)),
                ('telephone', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('address_info', models.TextField()),
                ('locality', models.TextField()),
                ('state', models.TextField()),
                ('post_code', models.CharField(max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderConfirmed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_purchase', models.DateTimeField(default=django.utils.timezone.now)),
                ('payment_method', models.TextField()),
                ('to_pay', models.FloatField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DietOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('megabytes', models.IntegerField()),
                ('days', models.IntegerField()),
                ('to_pay', models.FloatField()),
                ('delivery_cost', models.FloatField()),
                ('diet_cost', models.FloatField()),
                ('delivery_cost_per_day', models.FloatField()),
                ('diet_cost_per_day', models.FloatField()),
                ('date_of_start', models.DateField()),
                ('date_of_end', models.DateField()),
                ('address', models.CharField(max_length=100)),
                ('address_info', models.CharField(max_length=50)),
                ('locality', models.CharField(max_length=25)),
                ('state', models.CharField(max_length=25)),
                ('post_code', models.CharField(max_length=8)),
                ('distance', models.FloatField()),
                ('is_purchased', models.BooleanField(default=False)),
                ('confirmed_order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='checkout.orderconfirmed')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='menu.diet')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
