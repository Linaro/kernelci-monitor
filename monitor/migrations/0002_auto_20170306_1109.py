# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 11:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='kernelcijob',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
