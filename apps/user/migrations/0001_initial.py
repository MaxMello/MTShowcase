# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-16 18:47
from __future__ import unicode_literals

import apps.user.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Social',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('display_name', models.CharField(max_length=50)),
                ('icon', models.TextField(default='circle-o', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(blank=True, max_length=50, null=True)),
                ('unique_name', models.CharField(max_length=60, unique=True)),
                ('profile_img', models.ImageField(blank=True, default='/static/images/demoavatar.png', null=True, upload_to=apps.user.models.user_directory_path)),
                ('show_clear_name', models.BooleanField(default=True)),
                ('type', models.CharField(choices=[('student', 'Student'), ('professor', 'Professor'), ('admin', 'Admin')], default='student', max_length=25)),
                ('auth_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSocial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('social', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Social')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='socials',
            field=models.ManyToManyField(related_name='user_social', through='user.UserSocial', to='user.Social'),
        ),
    ]
