# Generated by Django 4.2.3 on 2023-07-16 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_rename_class_fromclass'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='is_private',
        ),
        migrations.RemoveField(
            model_name='room',
            name='limited_for',
        ),
        migrations.RemoveField(
            model_name='user',
            name='from_class',
        ),
        migrations.DeleteModel(
            name='FromClass',
        ),
    ]