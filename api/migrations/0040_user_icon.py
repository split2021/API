# Generated by Django 2.2.10 on 2020-06-02 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_auto_20200518_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='icon',
            field=models.ImageField(default='', upload_to=''),
            preserve_default=False,
        ),
    ]
