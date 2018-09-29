from django.urls import reverse
from .forms import AuthenticationForm, AdminAuthenticationForm
from urllib.parse import urlparse, urlunparse
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout,
)
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView


class SuccessURLAllowedHostsMixin:
    success_url_allowed_hosts = set()

    def get_success_url_allowed_hosts(self):
        return {self.request.get_host(), *self.success_url_allowed_hosts}

class LoginView(SuccessURLAllowedHostsMixin, FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm
    authentication_form = None
    redirect_field_name = REDIRECT_FIELD_NAME
    redirect_authenticated_user = False
    extra_context = None
    login_success_url = 'vm:index'


    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):  # 登录成功后跳转的地址
        url = self.get_redirect_url()
        return url or reverse(self.login_success_url)


    def get_redirect_url(self):     # 如果安全，将返回登录请求中的重定向地址
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''


    def get_form_class(self):   # 获取登录表单
        return self.authentication_form or self.form_class


    def get_form_kwargs(self):  # 返回用于实例化表单的关键字参数
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


    def form_valid(self, form): # 获取登录数据
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update({
            self.redirect_field_name: self.get_redirect_url(),
            'title': '登录',
            'site': current_site,
            'site_name': current_site.name,
            **(self.extra_context or {})
        })
        return context

class LogoutView(SuccessURLAllowedHostsMixin, TemplateView):
    next_page = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = ''
    extra_context = None
    logout_success_url = 'user:login'   # 退出后默认重定向地址


    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        auth_logout(request)
        next_page = self.get_next_page()
        if next_page:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        """Logout may be done via POST."""
        return self.get(request, *args, **kwargs)


    def get_next_page(self):    #  登出后的重定向地址
        if self.next_page is not None:
            next_page = resolve_url(self.next_page)
        elif self.logout_success_url:
            next_page = reverse(self.logout_success_url)
        else:
            next_page = self.next_page

        if (self.redirect_field_name in self.request.POST or
                self.redirect_field_name in self.request.GET):
            next_page = self.request.POST.get(
                self.redirect_field_name,
                self.request.GET.get(self.redirect_field_name)
            )
            url_is_safe = is_safe_url(
                url=next_page,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            # Security check -- Ensure the user-originating redirection URL is
            # safe.
            if not url_is_safe:
                next_page = self.request.path
        return next_page


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update({
            'site': current_site,
            'site_name': current_site.name,
            'title': 'Logged out',
            **(self.extra_context or {})
        })
        return context

def logout_then_login(request, login_url=None):
    """
    将登录的用户注销（重复登录挤下线）
    """
    login_url = reverse('user:login')
    return LogoutView.as_view(next_page=login_url)(request)


def redirect_to_login(next, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Redirect the user to the login page, passing the given 'next' page.
    """
    resolved_url = reverse('user:login')

    login_url_parts = list(urlparse(resolved_url))
    if redirect_field_name:
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring[redirect_field_name] = next
        login_url_parts[4] = querystring.urlencode(safe='/')

    return HttpResponseRedirect(urlunparse(login_url_parts))



class Site:
    # Text to put at the end of each page's <title>.
    site_title = 'Kvm站点管理员'
    # Text to put in each page's <h1>.
    site_header = 'Kvm 管理'
    # Text to put at the top of the admin index page.
    index_title = 'Site administration'
    # URL for the "View site" link at the top of each admin page.
    site_url = '/'


    def __init__(self, name='index_site'):
        self.name = name


    def each_context(self, request):
        script_name = request.META['SCRIPT_NAME']
        site_url = script_name if self.site_url == '/' and script_name else self.site_url
        return {
            'site_title': self.site_title,
            'site_header': self.site_header,
            'site_url': site_url,
            'has_permission': self.has_permission(request),
            'available_apps': '',   #  已注册应用列表
        }

    def has_permission(self, request):
        # 用户是有效的并且有权限，则返回True
        return request.user.is_active and request.user.is_staff


    @never_cache
    def login(self,request, extra_context=None):
        # 已登录则重定向到主页
        if request.method == 'GET' and (request.user.is_active and request.user.is_staff):
            index_path = reverse('vm:index', current_app='user')
            return HttpResponseRedirect(index_path)

        context = {
            **self.each_context(request),
            'title': '登录',
            'app_path': request.get_full_path(),
            'username': request.user.get_username(),
        }
        # 如果没有next则重定向到主页
        if (REDIRECT_FIELD_NAME not in request.GET and
                REDIRECT_FIELD_NAME not in request.POST):
            context[REDIRECT_FIELD_NAME] = reverse('vm:index', current_app='user')
        context.update(extra_context or {})
        defaults = {
            'extra_context': context,
            'authentication_form': AdminAuthenticationForm,
            'template_name': 'login.html',
        }
        request.current_app = 'user'
        return LoginView.as_view(**defaults)(request)




'''
@never_cache
def logout(self, request, extra_context=None):
"""
Log out the user for the given HttpRequest.

This should *not* assume the user is already logged in.
"""
from django.contrib.auth.views import LogoutView
defaults = {
    'extra_context': {
        **self.each_context(request),
        # Since the user isn't logged out at this point, the value of
        # has_permission must be overridden.
        'has_permission': False,
        **(extra_context or {})
    },
}
if self.logout_template is not None:
    defaults['template_name'] = self.logout_template
request.current_app = self.name
return LogoutView.as_view(**defaults)(request)

@never_cache
def login(self, request, extra_context=None):
"""
Display the login form for the given HttpRequest.
"""
if request.method == 'GET' and self.has_permission(request):
    # Already logged-in, redirect to admin index
    index_path = reverse('admin:index', current_app=self.name)
    return HttpResponseRedirect(index_path)

from django.contrib.auth.views import LoginView
# Since this module gets imported in the application's root package,
# it cannot import models from other applications at the module level,
# and django.contrib.admin.forms eventually imports User.
from django.contrib.admin.forms import AdminAuthenticationForm
context = {
    **self.each_context(request),
    'title': _('Log in'),
    'app_path': request.get_full_path(),
    'username': request.user.get_username(),
}
if (REDIRECT_FIELD_NAME not in request.GET and
        REDIRECT_FIELD_NAME not in request.POST):
    context[REDIRECT_FIELD_NAME] = reverse('admin:index', current_app=self.name)
context.update(extra_context or {})

defaults = {
    'extra_context': context,
    'authentication_form': self.login_form or AdminAuthenticationForm,
    'template_name': self.login_template or 'admin/login.html',
}
request.current_app = self.name
return LoginView.as_view(**defaults)(request)
'''

# 修改自带的后台管理tag
from django.contrib import admin
admin.site.site_title="Kvm后台管理员"
admin.site.site_header="Kvm后台管理"