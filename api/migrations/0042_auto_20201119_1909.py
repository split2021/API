# Generated by Django 3.1 on 2020-11-19 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20200602_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pro',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]