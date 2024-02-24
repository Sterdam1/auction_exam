# Generated by Django 5.0.2 on 2024-02-24 07:46

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotlist', '0012_alter_lot_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='lot',
            name='end_time',
            field=models.DurationField(default=datetime.timedelta(days=1), help_text='Укажите сколько будет длиться аукцион', verbose_name='Длительность аукциона'),
        ),
        migrations.AlterField(
            model_name='lot',
            name='ready_status',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='lotlist.readyornot', verbose_name='Готовность лота'),
        ),
    ]
