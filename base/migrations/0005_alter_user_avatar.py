# Generated by Django 4.0.5 on 2022-07-16 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='https://res.cloudinary.com/hcwyrgltb/image/upload/v1657960650/images/avatars/avatar_e7rnoq.svg', null=True, upload_to='avatars'),
        ),
    ]