# Generated by Django 4.2.3 on 2024-03-08 14:20

import base.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0042_remove_user_school_year_user_updated_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='file',
            field=models.ImageField(blank=True, max_length=512, null=True, upload_to='', validators=[base.models.validate_image], verbose_name='room_image'),
        ),
    ]
