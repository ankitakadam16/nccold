# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-06-20 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0008_auto_20200620_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='gst',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]