# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-06-11 17:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ERP', '0005_auto_20200603_2144'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetAllocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('codeHead', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=500)),
                ('allotmentAmount', models.FloatField(default=0.0)),
                ('withdrawalAmount', models.FloatField(default=0.0)),
                ('balance', models.FloatField(default=0.0)),
                ('allotedBy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alloterUser', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='budget_parent', to='ERP.BudgetAllocation')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unitUser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='vendor',
            name='phone',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
