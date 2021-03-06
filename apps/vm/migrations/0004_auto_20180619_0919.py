# Generated by Django 2.1a1 on 2018-06-19 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vm', '0003_auto_20180615_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vm_info',
            name='ip',
            field=models.GenericIPAddressField(protocol='ipv4', verbose_name='IP'),
        ),
        migrations.AlterField(
            model_name='vm_info',
            name='name',
            field=models.CharField(max_length=100, verbose_name='名称'),
        ),
    ]
