from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from .models import EmailDevice
from .forms import EmailDeviceForm
from apps.core.utils import generate_password
import random

class MailRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perm('emaildevice.emaildevice_access')

class MailDeviceBaseMixin(LoginRequiredMixin, MailRequiredMixin):
    model = EmailDevice
    success_url = reverse_lazy('emaildevice:list')

    def get_queryset(self):
        return EmailDevice.objects.filter(
            owner=self.request.user,
            status=EmailDevice.Status.ACTIVE
        ).order_by('created_at')

class EmailDeviceList(MailDeviceBaseMixin, ListView):
    template_name = 'emaildevice/emaildevice_list.html'
    context_object_name = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EmailDeviceForm()
        context['deactivate_ldap_login'] = settings.EMAILDEVICE_SETTINGS.get('DEACTIVATE_LDAP_LOGIN_AFTER_CREATE')
        return context

class EmailDeviceCreate(MailDeviceBaseMixin, CreateView):
    form_class = EmailDeviceForm

    def form_valid(self, form):
        if not EmailDevice.check_account_limit(self.request.user):
            messages.error(
                self.request,
                f'Limit von {settings.EMAILDEVICE_SETTINGS["MAX_ACCOUNTS"]} Accounts erreicht!'
            )
            return redirect(self.success_url)

        account = form.save(commit=False)
        account.owner = self.request.user

        split_parts = self.request.user.username.split('@')
        localpart = split_parts[0]
        domain = split_parts[1] if len(split_parts) > 1 else settings.EMAILDEVICE_SETTINGS['REALM']

        account.username = EmailDevice.generate_unique_username(localpart, domain=domain)
        password = generate_password(settings.EMAILDEVICE_SETTINGS["PASSWORD_LENGTH"])
        account.password = password
        account.save()
        messages.info(
            self.request, 
            f"{account.username}|{password}",
            extra_tags='credentials'
        )
        return redirect(self.success_url)

class EmailDeviceDelete(MailDeviceBaseMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        account = self.get_object()
        username = account.username
        account.status = EmailDevice.Status.DELETED
        account.save()
        messages.success(request, f"Account {username} wurde gelöscht")
        return redirect(self.success_url)

class EmailDeviceUpdate(MailDeviceBaseMixin, UpdateView):
    fields = []
    
    def form_valid(self, form):
        account = self.object
        password = generate_password(settings.EMAILDEVICE_SETTINGS["PASSWORD_LENGTH"])
        account.password = password
        account.save()
        messages.success(
            self.request,
            f"{account.username}|{password}",
            extra_tags='credentials'
        )
        return redirect('emaildevice:list')