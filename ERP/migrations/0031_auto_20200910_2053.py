# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-09-10 15:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0030_auto_20200909_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetallocation',
            name='allotment_no',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='budgetallocation',
            name='description',
            field=models.CharField(max_length=5000, null=True),
        ),
    ]
