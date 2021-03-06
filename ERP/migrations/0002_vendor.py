# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-05-17 07:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ERP', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.TextField(max_length=200, null=True)),
                ('pincode', models.PositiveIntegerField(default=0)),
                ('gst', models.CharField(max_length=100, null=True)),
                ('bankACno', models.PositiveIntegerField(default=0)),
                ('ifsc', models.CharField(max_length=100, null=True)),
                ('properiterName', models.CharField(max_length=100, null=True)),
                ('panNumber', models.CharField(max_length=100, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vendorUser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
