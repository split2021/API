# Generated by Django 3.1 on 2020-12-10 16:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_modelapiview.JSONMixin


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0043_auto_20201119_2327'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menus', to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, django_modelapiview.JSONMixin),
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('price', models.FloatField(default=0)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='api.menu')),
            ],
            bases=(models.Model, django_modelapiview.JSONMixin),
        ),
    ]
