from django.contrib import admin
from .models import VmInfo

# Register your models here.

class vminfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'name', 'ip', 'user', 'iso_ver',
                    'package', 'purposes', 'remark', 'created_at', 'status')


admin.site.register(VmInfo, vminfoAdmin)