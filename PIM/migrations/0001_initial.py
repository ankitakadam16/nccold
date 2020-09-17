# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2020-01-21 15:39
from __future__ import unicode_literals

import PIM.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ERP', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        migrations.CreateModel(
            name='chatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=200, null=True)),
                ('attachment', models.FileField(null=True, upload_to=PIM.models.getChatMessageAttachment)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('originator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sentIMs', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('emailSecondary', models.EmailField(max_length=254, null=True)),
                ('mobile', models.CharField(max_length=12, null=True)),
                ('mobileSecondary', models.CharField(max_length=12, null=True)),
                ('designation', models.CharField(max_length=30, null=True)),
                ('notes', models.TextField(max_length=300, null=True)),
                ('linkedin', models.CharField(max_length=100, null=True)),
                ('facebook', models.CharField(max_length=100, null=True)),
                ('dp', models.FileField(null=True, upload_to=PIM.models.getClientRelationshipContactDP)),
                ('male', models.BooleanField(default=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contactsPIM', to='ERP.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contactsuser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='notebook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=500, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notebooks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(max_length=300, null=True)),
                ('link', models.URLField(max_length=100, null=True)),
                ('shortInfo', models.CharField(max_length=250, null=True)),
                ('read', models.BooleanField(default=False)),
                ('domain', models.CharField(choices=[(b'System', b'System'), (b'Administration', b'Administration'), (b'Application', b'Application')], default=b'SYS', max_length=3)),
                ('originator', models.CharField(max_length=20, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('onHold', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('source', models.TextField(max_length=1000000, null=True)),
                ('title', models.CharField(max_length=500, null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='PIM.notebook')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notebookPages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('presence', models.CharField(choices=[(b'NA', b'NA'), (b'Available', b'Available'), (b'Busy', b'Busy'), (b'Away', b'Away'), (b'On Leave', b'On Leave'), (b'In A Meeting', b'In a meeting')], default=b'NA', max_length=15)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main', models.CharField(max_length=10, null=True)),
                ('highlight', models.CharField(max_length=10, null=True)),
                ('background', models.CharField(max_length=10, null=True)),
                ('backgroundImg', models.ImageField(null=True, upload_to=PIM.models.getThemeImageUploadPath)),
                ('parent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='theme', to='PIM.settings')),
            ],
        ),
    ]
