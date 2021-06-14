# Generated by Django 3.2.4 on 2021-06-14 22:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('menu', '0002_delete_dietorder'),
    ]

    operations = [
        migrations.CreateModel(
            name='DietOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('megabytes', models.IntegerField()),
                ('days', models.IntegerField()),
                ('date_of_start', models.DateField(default=django.utils.timezone.now)),
                ('day_of_end', models.DateField()),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='menu.diet')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
