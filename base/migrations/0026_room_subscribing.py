# Generated by Django 4.2.3 on 2024-01-11 10:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0025_delete_reportlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='subscribing',
            field=models.ManyToManyField(related_name='room_users_subs', to=settings.AUTH_USER_MODEL),
        ),
    ]
