# Generated by Django 4.2.3 on 2023-07-12 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_user_liked_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='likes',
        ),
        migrations.RemoveField(
            model_name='user',
            name='liked_message',
        ),
    ]
