# Generated by Django 2.2.1 on 2019-05-28 15:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import eip.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('date', models.DateTimeField()),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectLogDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('KO', 'Kick off'), ('FU', 'Follow up'), ('D', 'Delviery')], max_length=2)),
                ('file', models.FileField(upload_to=eip.models.get_pld_path)),
                ('meeting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='eip.Meeting')),
            ],
        ),
    ]
