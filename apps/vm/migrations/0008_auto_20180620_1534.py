# Generated by Django 2.1a1 on 2018-06-20 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vm', '0007_auto_20180620_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vm_info',
            name='created_at',
            field=models.CharField(blank=True, max_length=100, verbose_name='创建时间'),
        ),
    ]
