# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-05-17 17:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ERP', '0003_auto_20200517_0835'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('denominator', models.CharField(max_length=200, null=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('rate', models.FloatField(default=0.0)),
                ('amount', models.FloatField(default=0.0)),
                ('gst', models.FloatField(default=0.0)),
                ('gstAmount', models.FloatField(default=0.0)),
                ('grandTotal', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='PoOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.TextField(max_length=200, null=True)),
                ('total', models.FloatField(default=0.0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='poUser', to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vendorName', to='ERP.Vendor')),
            ],
        ),
        migrations.AddField(
            model_name='poitems',
            name='po',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='poName', to='ERP.PoOrder'),
        ),
    ]