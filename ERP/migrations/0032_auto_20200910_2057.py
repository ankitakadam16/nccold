# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-09-10 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0031_auto_20200910_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='poorder',
            name='majorHead',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='poorder',
            name='workOrderDate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='poorder',
            name='workOrderNo',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
