# Generated by Django 4.2.3 on 2024-03-03 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0041_alter_room_file_alter_room_name_alter_topic_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='school_year',
        ),
        migrations.AddField(
            model_name='user',
            name='updated_profile',
            field=models.BooleanField(default=True),
        ),
    ]
