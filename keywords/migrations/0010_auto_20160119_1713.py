# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-19 22:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('keywords', '0009_auto_20160119_1712'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='result',
            options={'ordering': ('keyword', 'word_count', 'url')},
        ),
    ]