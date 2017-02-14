# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-13 13:38
from __future__ import unicode_literals

import apps.project.models
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectContentRevision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revision_date', models.DateTimeField(auto_now_add=True)),
                ('project_image', models.ImageField(default='/static/images/default_project_image.jpg', upload_to=apps.project.models.project_directory_path)),
                ('project_image_cropped', models.ImageField(default='/static/images/default_project_image.jpg', upload_to=apps.project.models.project_directory_path)),
                ('heading', models.CharField(max_length=100)),
                ('subheading', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=2000)),
                ('contents', jsonfield.fields.JSONField(default='[]')),
                ('supervisor_comment', models.TextField(blank=True, max_length=2000, null=True)),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.User')),
            ],
        ),
        migrations.RemoveField(
            model_name='projectcontent',
            name='project',
        ),
        migrations.AddField(
            model_name='project',
            name='contents',
            field=jsonfield.fields.JSONField(default='[]'),
        ),
        migrations.AddField(
            model_name='project',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='year_from',
            field=models.IntegerField(choices=[(1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017)], default=2017),
        ),
        migrations.AlterField(
            model_name='project',
            name='year_to',
            field=models.IntegerField(choices=[(1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017)], default=2017),
        ),
        migrations.DeleteModel(
            name='ProjectContent',
        ),
        migrations.AddField(
            model_name='projectcontentrevision',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project'),
        ),
    ]
