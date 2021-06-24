# Generated by Django 3.2.4 on 2021-06-24 18:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menu', '0002_delete_dietorder'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DietOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('megabytes', models.IntegerField()),
                ('days', models.IntegerField(null=True)),
                ('date_of_start', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_of_end', models.DateTimeField()),
                ('address', models.TextField()),
                ('address_info', models.TextField()),
                ('locality', models.TextField()),
                ('state', models.TextField()),
                ('post_code', models.TextField()),
                ('is_finished', models.BooleanField(default=False)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='menu.diet')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
