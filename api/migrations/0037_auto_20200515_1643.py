# Generated by Django 2.2.10 on 2020-05-15 14:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_auto_20200515_1640'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='curreny',
            new_name='currency',
        ),
    ]
