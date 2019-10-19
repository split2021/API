# Generated by Django 2.2.2 on 2019-06-24 15:25

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_remove_log_cookies'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='cookies',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=''),
            preserve_default=False,
        ),
    ]