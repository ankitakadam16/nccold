# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-09-10 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0032_auto_20200910_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poorder',
            name='supplyOrderNo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='poorder',
            name='workOrderNo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
