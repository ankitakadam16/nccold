# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-07-05 14:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0011_budgetallocation_minorhead'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetallocation',
            name='is_withdrawn',
            field=models.BooleanField(default=True),
        ),
    ]