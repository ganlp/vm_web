# Generated by Django 2.1a1 on 2018-06-19 09:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vm', '0004_auto_20180619_0919'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vm_info',
            old_name='ios_ver',
            new_name='iso_ver',
        ),
    ]
