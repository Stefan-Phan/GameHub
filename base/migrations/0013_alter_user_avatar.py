# Generated by Django 5.0.7 on 2024-08-26 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='static/images/default-avatar.png', null=True, upload_to=''),
        ),
    ]
