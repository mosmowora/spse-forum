# Generated by Django 4.2.3 on 2023-09-27 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_alter_fromclass_set_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fromclass',
            name='set_class',
            field=models.CharField(max_length=30),
        ),
    ]