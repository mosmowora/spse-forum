# Generated by Django 4.2.3 on 2023-10-06 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_alter_message_body'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-updated', '-created']},
        ),
    ]
