# Generated by Django 4.2.3 on 2023-07-15 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_class_room_limited_for'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='name',
            field=models.CharField(max_length=5, unique=True),
        ),
    ]