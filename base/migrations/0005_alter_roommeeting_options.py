# Generated by Django 5.0.7 on 2024-08-03 01:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_roommeeting'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roommeeting',
            options={'ordering': ['-update', '-created']},
        ),
    ]
