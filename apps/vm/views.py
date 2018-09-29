from django.shortcuts import render, HttpResponse
from .forms import SearchForm,AddFrom
from .models import VmInfo, VmLog, VmHardware
from .fun import comments
from django.views.generic import View, FormView, TemplateView, DetailView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from vm_web.settings import HOST
from django.db.models import Q


def visitor_ip(request):    # 获取访问IP
    if request:
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
    else:
        ip = ''
    return ip

def writelog(data):     # 写日志
    obj = VmLog.objects
    obj.create(type=data['type'], content=data['content'], created_by=data['created_by'], ip=data['ip'])

class IndexDisplay(TemplateView):
    model = VmInfo
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['data'] = self.model.objects.all().order_by('-created_at')
        return context


class Index(FormView):
    #from django.contrib.auth.decorators import login_required
    #from django.utils.decorators import method_decorator
    #@method_decorator(login_required)
    template_name = 'index.html'
    form_class = SearchForm
    model = VmInfo
    host = HOST

    def _search(self, keyword):     # 表单查询
        keyl = [key for key in keyword.keys() if keyword[key]]  # 筛选不为空的表单
        q = Q()
        for key in keyl:
            if key == 'host':
                q &= Q(host__icontains='kvm%s' % keyword[key]) if keyword[key] != '9' else ~Q(
                    host__in=['kvm1', 'kvm2', 'kvm3', 'kvm4', 'kvm5'])
                continue
            elif key == 'status':
                q &= Q(status__icontains='%s' % {'1': '运行中', '2': '关闭', '3': '不存在'}[keyword['status']])
                continue
            elif key == 'description':
                q &= Q(purposes__icontains=keyword['description']) | Q(remark__icontains=keyword['description'])
                continue
            q &= Q(**{'%s__icontains' % key: keyword[key]})

        return self.model.objects.filter(q)

    def _run(self, action, vm_id):     # 开关机
        info = self.model.objects.get(id=vm_id)
        ret = comments.running(info.name, self.host[info.host], action)
        if ret:
            return ret
        else:
            ret = 0
            status = [i for i in ['运行中', '关闭'] if i != info.status]
            msg = '[%s] - %s(%s)' % ('开机' if action == 'on' else '关机', info.name, info.ip)
            writelog({'type': 'Update', 'content': msg, 'created_by': 'admin', 'ip': visitor_ip(self.request)})
            self.model.objects.filter(id=vm_id).update(status=status[0])

        return ret

    def get(self, request, *args, **kwargs):
        # 获取表单传递过来的参数，保存为下一次的表单初始数据回显
        form_values = request.GET.copy()
        self.initial = {
            'host': form_values.get('host'),
            'name': form_values.get('name'),
            'ip': form_values.get('ip'),
            'status': form_values.get('status'),
            'description': form_values.get('description')}

        data = self.model.objects.all()
        if form_values:
            data = self._search(self.initial.copy())

        paginator = Paginator(data.order_by('-created_at'), 30)  # 默认30分页
        page = request.GET.get('page')
        data = paginator.get_page(page)
        context = self.get_context_data(**kwargs)
        context['data'] = data

        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        values = request.POST.copy()
        ret = None
        if values.get('btn-on'):
            ret = self._run('on', values.get('btn-on'))
        elif values.get('btn-off'):
            ret = self._run('off', values.get('btn-off'))
        return HttpResponse(ret)


class UserLogDisplay(TemplateView):
    model = VmLog
    template_name = 'userlog.html'

    def get(self, request, *args, **kwargs):
        log_list = self.model.objects.all().order_by('-created_at')
        paginator = Paginator(log_list, 25)     # 默认25分页
        page = request.GET.get('page')
        data = paginator.get_page(page)


        context = self.get_context_data(**kwargs)
        context['data'] = data
        return self.render_to_response(context)


class Create(FormView):
    template_name = 'create.html'
    form_class = AddFrom
    model = VmInfo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddFrom()
        messages.warning(self.request, '暂不可用.')
        return context

    def form_valid(self, form):
        return HttpResponse('禁止创建！')


class KvmDetial(DetailView):
    model = VmHardware
    template_name = "vm_detail.html"


    def get_object(self, queryset=None):
        vm_id = self.kwargs.get(self.pk_url_kwarg)
        obj = self.model.objects.filter(vm_id=vm_id)
        if not obj:
            vm = VmInfo.objects.filter(pk=vm_id)
            if vm:
                vm = vm.get()
                obj = self.model.objects.filter(host=vm.host, domain=vm.name)
        try:
            obj = obj.get()
            if obj.vm_id != vm_id:
                obj.vm_id = vm_id
                obj.save()
        except Exception:
            obj = ''
        return obj


class AutoStartList(TemplateView):
    template_name = 'autostart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        namelist, errlist = comments.show_autostart()
        for i in errlist:
            messages.warning(self.request, '获取%s服务器数据失败.' % i)
        data = []
        for host, xmls in namelist.items():
            for xml in xmls:
                name = VmHardware.objects.filter(host=host,xml=xml)
                name = name.get().domain if name else 'Unknown'
                ip = VmInfo.objects.filter(host=host, name=name)
                ip = ip.get().ip if ip else 'Unknown'
                data.append({'host': host, 'xml_file': xml, 'name': name, 'ip': ip})
        context['data'] = data
        return context


    def get(self, request, *args, **kwargs):

        action = request.GET.get('action')
        host = request.GET.get('host')
        name = request.GET.get('name')
        ip = request.GET.get('ip')
        if action == 'del':
            if host and name:
                result = comments.autostart(name,host)
                if not result:
                    messages.success(request, '操作成功,%s已取消开机自启动.' % name)
                    msg = '[取消]-%s 开机自启动.' % name
                    writelog({'type': 'Delete', 'content': msg, 'created_by': 'admin', 'ip': visitor_ip(request)})
                else: messages.warning(request, '操作失败:%s.' % result)
                return HttpResponseRedirect('/autostart/')

        elif action == 'add':
            if host and name:
                result = comments.autostart(name,host,True)
            elif ip:
                obj = VmInfo.objects.filter(ip=ip)
                if len(obj) == 1:
                    obj = obj.get()
                    name = obj.name
                    host = obj.host
                    result = comments.autostart(name, host, True)
                else:
                    result = 'IP不存在，或者有多个相同的IP存在!'
            else:
                result = '参数错误!'
            if not result:
                messages.success(request, '操作成功,%s已添加开机自启动.' % name)
                msg = '[添加]-%s 开机自启动.' % name
                writelog({'type': 'Create', 'content': msg, 'created_by': 'admin', 'ip': visitor_ip(request)})
            else:
                messages.warning(request, '操作失败:%s.' % result)
            return HttpResponseRedirect('/autostart/')


        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class TestHtml(View):
    template_name = 'test.html'

    def post(self, request, *args, **kwargs):
        print(request.body)
        return HttpResponse(345)

    def get(self, request, *args, **kwargs):
        #return HttpResponse('<a href="/logout/">注销</a>')
        messages.success(request, '！')
        return render(request,self.template_name)

