# Generated by Django 2.2.1 on 2019-06-16 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_user_friends'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment_user',
            old_name='name',
            new_name='mastercard',
        ),
        migrations.AddField(
            model_name='payment_user',
            name='cvc',
            field=models.CharField(default='None', max_length=4),
        ),
        migrations.AddField(
            model_name='payment_user',
            name='expirancy',
            field=models.CharField(default='None', max_length=10),
        ),
    ]