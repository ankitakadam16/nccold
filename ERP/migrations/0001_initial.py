# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2020-01-21 15:39
from __future__ import unicode_literals

import ERP.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=300, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('state', models.CharField(max_length=50, null=True)),
                ('pincode', models.PositiveIntegerField(null=True)),
                ('lat', models.CharField(max_length=15, null=True)),
                ('lon', models.CharField(max_length=15, null=True)),
                ('country', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ApiUsage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField(default=0)),
                ('month', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('icon', models.CharField(max_length=20, null=True)),
                ('haveCss', models.BooleanField(default=True)),
                ('haveJs', models.BooleanField(default=True)),
                ('inMenu', models.BooleanField(default=True)),
                ('description', models.CharField(max_length=500)),
                ('canConfigure', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='canBeConfigureFrom', to='ERP.application')),
            ],
        ),
        migrations.CreateModel(
            name='appSettingsField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
                ('flag', models.BooleanField(default=False)),
                ('value', models.CharField(max_length=5000, null=True)),
                ('description', models.CharField(max_length=500)),
                ('fieldType', models.CharField(choices=[('flag', 'flag'), ('value', 'value')], default='flag', max_length=5)),
                ('app', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='ERP.application')),
            ],
        ),
        migrations.CreateModel(
            name='device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sshKey', models.CharField(max_length=500, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='groupPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ERP.application')),
                ('givenBy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approvedGroupAccess', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accessibleApps', to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('link', models.TextField(max_length=300, null=True)),
                ('attachment', models.FileField(null=True, upload_to=ERP.models.getERPPictureUploadPath)),
                ('mediaType', models.CharField(choices=[('onlineVideo', 'onlineVideo'), ('video', 'video'), ('image', 'image'), ('onlineImage', 'onlineImage'), ('doc', 'doc')], default='image', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='serviceDocsUploaded', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(max_length=500)),
                ('icon', models.CharField(max_length=20, null=True)),
                ('haveCss', models.BooleanField(default=True)),
                ('haveJs', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='ERP.application')),
                ('givenBy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approvedAccess', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accessibleApps', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('devices', models.ManyToManyField(to='ERP.device')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gitProfile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PublicApiKeys',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=False)),
                ('key', models.CharField(max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('usageRemaining', models.PositiveIntegerField(default=0)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apiKeyAdministrator', to=settings.AUTH_USER_MODEL)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ERP.application')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publicApiKeysOwned', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('mobile', models.CharField(max_length=20, null=True)),
                ('telephone', models.CharField(max_length=20, null=True)),
                ('about', models.TextField(max_length=2000, null=True)),
                ('cin', models.CharField(max_length=100, null=True)),
                ('tin', models.CharField(max_length=100, null=True)),
                ('logo', models.CharField(max_length=200, null=True)),
                ('web', models.TextField(max_length=100, null=True)),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ERP.address')),
                ('contactPerson', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='servicesContactPerson', to=settings.AUTH_USER_MODEL)),
                ('doc', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='ERP.media')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicesCreated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='application',
            name='module',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='apps', to='ERP.module'),
        ),
        migrations.AddField(
            model_name='application',
            name='owners',
            field=models.ManyToManyField(blank=True, related_name='appsManaging', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='apiusage',
            name='api',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usages', to='ERP.PublicApiKeys'),
        ),
        migrations.AlterUniqueTogether(
            name='appsettingsfield',
            unique_together=set([('name', 'app')]),
        ),
    ]
