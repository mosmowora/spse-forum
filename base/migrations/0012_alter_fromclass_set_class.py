# Generated by Django 4.2.3 on 2023-09-27 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_remove_user_status_remove_user_status_del_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fromclass',
            name='set_class',
            field=models.CharField(max_length=10),
        ),
    ]
