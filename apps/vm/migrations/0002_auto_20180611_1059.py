# Generated by Django 2.1a1 on 2018-06-11 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vmdetails',
            name='host',
            field=models.CharField(max_length=20, verbose_name='主机'),
        ),
        migrations.AlterField(
            model_name='vmdetails',
            name='vm_ip',
            field=models.CharField(max_length=50, verbose_name='IP'),
        ),
        migrations.AlterField(
            model_name='vmdetails',
            name='vm_name',
            field=models.CharField(max_length=100, verbose_name='名称'),
        ),
        migrations.AlterField(
            model_name='vmdetails',
            name='vm_status',
            field=models.CharField(max_length=20, verbose_name='状态'),
        ),
    ]
