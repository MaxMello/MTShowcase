# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-03-05 23:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_auto_20170225_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='C:/Users/dirk/Desktop/images')),
            ],
        ),
    ]