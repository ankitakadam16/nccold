# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-06-03 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0004_auto_20200517_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='phone',
            field=models.PositiveIntegerField(default=0, max_length=100),
        ),
    ]
