# Generated by Django 4.2.3 on 2023-08-25 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_alter_fromclass_set_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='limited_for',
            field=models.ManyToManyField(related_name='room_limited_for', to='base.fromclass'),
        ),
    ]
