# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2020-08-23 02:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0021_auto_20200822_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=500)),
                ('rank', models.CharField(max_length=200)),
                ('serviceNo', models.CharField(max_length=100)),
                ('typ', models.CharField(max_length=100)),
            ],
        ),
    ]
