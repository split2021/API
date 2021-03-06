# Generated by Django 2.2.2 on 2019-06-24 14:15

import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20190624_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('path', models.CharField(max_length=255)),
                ('method', models.CharField(max_length=10)),
                ('headers', django.contrib.postgres.fields.hstore.HStoreField()),
                ('body', models.TextField(default='')),
                ('cookies', django.contrib.postgres.fields.hstore.HStoreField()),
            ],
        ),
    ]
