#coding=utf-8
from django.db import models
import django.utils.timezone as timezone


class VmInfo(models.Model):
    host = models.CharField(verbose_name='主机', max_length=10)
    name = models.CharField(verbose_name='名称', max_length=100)
    iso_ver = models.CharField(verbose_name='系统版本', max_length=100, blank=True)
    package = models.CharField(verbose_name='镜像版本', max_length=100, blank=True)
    user = models.CharField(verbose_name='申请人', max_length=20, blank=True)
    purposes = models.CharField(verbose_name='用途', max_length=100)
    remark = models.CharField(verbose_name='备注', max_length=200, blank=True)
    created_at = models.DateField('创建时间', default=timezone.now,blank=True, null=True)
    updated_at = models.DateTimeField('修改时间', auto_now=True)
    ip = models.GenericIPAddressField('IP', protocol='ipv4')
    status = models.CharField(verbose_name='状态', max_length=10, blank=True)


class VmLog(models.Model):
    type = models.CharField(verbose_name='类型', max_length=10)
    content = models.CharField(verbose_name='内容', max_length=100)
    created_by = models.CharField(verbose_name='创建人', max_length=20)
    created_at = models.DateTimeField('创建时间', default=timezone.now,blank=True)
    ip = models.GenericIPAddressField('访问IP', protocol='ipv4')


class VmHardware(models.Model):
    detail_id = models.AutoField(primary_key=True)
    vm_id = models.IntegerField(blank=True,null=True)
    host = models.CharField(max_length=10)
    xml = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    uuid = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    memory = models.IntegerField()
    vcpu = models.IntegerField()
    storage = models.CharField(max_length=3000)
    network = models.CharField(max_length=3000)
    modified_time = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)










