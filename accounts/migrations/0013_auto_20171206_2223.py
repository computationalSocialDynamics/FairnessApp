# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-07 03:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20171130_1126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='desp',
        ),
        migrations.RemoveField(
            model_name='document',
            name='document',
        ),
        migrations.RemoveField(
            model_name='document',
            name='uploaded_at',
        ),
        migrations.AddField(
            model_name='document',
            name='link',
            field=models.CharField(default='', max_length=150),
        ),
    ]
