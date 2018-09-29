from django.forms import forms,fields,widgets
from django.core.validators import RegexValidator

class SearchForm(forms.Form):
    host = fields.ChoiceField(
        choices=((None,'全部'),(1,'kvm1'),(2,'kvm2'),(3,'kvm3'),(4,'kvm4'),(5,'kvm5'),(9,'其它')),
        label='主机',
        label_suffix='：',
        required=False,
        widget=fields.Select(
            attrs={'class': 'form-control d-inline col-1', 'style': 'min-width: 100px;'})
        #validators=[RegexValidator(r'[1-5]', '...')]
    )
    name = fields.CharField(required=False, label='名称', label_suffix='：', widget=fields.TextInput(
        attrs={'class': 'form-control d-inline col-2 font-weight-light', 'placeholder': '虚拟机名称',
               'style': 'min-width: 130px;'}))
    ip = fields.CharField(required=False, label='IP', label_suffix='：', widget=fields.TextInput(
        attrs={'class': 'form-control d-inline col-2 font-weight-light', 'placeholder': '虚拟机IP',
               'style': 'min-width: 130px;'}))
    status = fields.ChoiceField(
        choices=((None, '全部'),(1,'运行中'),(2,'关闭'),(3,'不存在')),
        label='状态',
        label_suffix='：',
        required=False,
        widget=fields.Select(
                attrs={'class': 'form-control d-inline col-1', 'style': 'min-width: 100px;'})
    )
    description = fields.CharField(required=False, label='描述', label_suffix='：', widget=fields.TextInput(
        attrs={'class': 'form-control d-inline col-2 font-weight-light', 'placeholder': '用途 or 备注',
               'style': 'min-width: 130px;'}))


class AddFrom(forms.Form):
    host = fields.ChoiceField(
        choices=((None, '请选择..'), (1, 'kvm1'), (2, 'kvm2'), (3, 'kvm3'), (4, 'kvm4'), (5, 'kvm5')),
        label='主机',
        label_suffix='：',
        widget=fields.Select(
            attrs={'class': 'form-control col-2'}),
        validators=[RegexValidator(r'[1-5]', '请选择待安装镜像的宿主机。')]
    )
    ver = fields.ChoiceField(
        choices=((None, '请选择..'), (1, 'v59'), (2, 'v60'), (3, 'v70'), (4, 'v80')),
        label='系统版本',
        label_suffix='：',
        widget=fields.Select(
            attrs={'class': 'form-control col-2'}),
        validators=[RegexValidator(r'[1-5]', '请选择待安装镜像的版本类别。')]
    )
    package = fields.CharField(label='镜像包', label_suffix='：', widget=fields.TextInput(
        attrs={'class': 'form-control col-4', 'placeholder': '镜像包全称，如v59-rc01-006-marketing-20151119-iso.tar.gz',
               'style': 'font-size: small'}))
    name = fields.CharField(label='虚拟机名称', label_suffix='：', widget=fields.TextInput(
        attrs={'class': 'form-control col-4', 'placeholder': '请输入待创建的虚拟机名称',
               'style': 'font-size: small'}))
    imgfile = fields.CharField(label='磁盘文件', label_suffix='：', widget=fields.TextInput(
        attrs={'class': 'form-control col-4', 'placeholder': '请输入待创建的磁盘文件名称',
               'style': 'font-size: small'}))
    ip = fields.CharField(label='IP', label_suffix='：', widget=fields.TextInput(
        attrs={'class': 'form-control col-4', 'placeholder': '请输入待指定的ip地址',
               'style': 'font-size: small'}))


class LicenseForm(forms.Form):
    pass
