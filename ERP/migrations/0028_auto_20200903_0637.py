# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2020-09-03 06:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0027_auto_20200827_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='phone',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
