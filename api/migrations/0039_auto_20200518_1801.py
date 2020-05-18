# Generated by Django 2.2.10 on 2020-05-18 16:01

import api.models
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_payment_target'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=42)),
            ],
            bases=(models.Model, api.models.JsonizableMixin),
        ),
        migrations.AddField(
            model_name='user',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='title',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='api.PaymentGroup'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payments',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.RenameModel(
        old_name='GroupMembership',
        new_name='PaymentGroupMembership',
        ),
        migrations.AlterField(
            model_name='PaymentGroupMembership',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.PaymentGroup'),
        ),
        migrations.DeleteModel(
            name='Group',
        ),
        migrations.AddField(
            model_name='PaymentGroup',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='payment_groups', through='api.PaymentGroupMembership', to=settings.AUTH_USER_MODEL),
        ),
    ]
