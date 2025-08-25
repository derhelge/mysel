from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from .models import IotDeviceAccount
from .forms import IotDeviceAccountForm
from apps.core.utils import generate_password

class IotDeviceRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perm('iotdevices.iotdevice_access')

class IotDeviceBaseMixin(LoginRequiredMixin, IotDeviceRequiredMixin):
    model = IotDeviceAccount
    success_url = reverse_lazy('iotdevices:list')

    def get_queryset(self):
        return IotDeviceAccount.objects.filter(
            owner=self.request.user,
            status=IotDeviceAccount.Status.ACTIVE
        )

class IotDeviceList(IotDeviceBaseMixin, ListView):
    template_name = 'iotdevices/iotdevice_list.html'
    context_object_name = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = IotDeviceAccountForm()
        return context

class IotDeviceCreate(IotDeviceBaseMixin, CreateView):
    form_class = IotDeviceAccountForm

    def form_valid(self, form):
        if not IotDeviceAccount.check_account_limit(self.request.user):
            messages.error(
                self.request,
                f'Limit von {settings.IOTDEVICE_SETTINGS["MAX_ACCOUNTS"]} Accounts erreicht!'
            )
            return redirect(self.success_url)

        account = form.save(commit=False)
        account.owner = self.request.user
        account.password=generate_password(8)
        account.save()
        
        messages.info(
            self.request, 
            f"{account.mac_address}|{account.password}|{account.device_name}",
            extra_tags='credentials'
        )
        return redirect(self.success_url)

class IotDeviceDetail(IotDeviceBaseMixin, DetailView):
    def get(self, request, *args, **kwargs):
        account = self.get_object()
        messages.info(
            request, 
            f"{account.mac_address}|{account.password}|{account.device_name}",
            extra_tags='credentials'
        )
        return redirect('iotdevices:list')

class IotDeviceDelete(IotDeviceBaseMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        account = self.get_object()
        mac_address = account.mac_address
        account.status = IotDeviceAccount.Status.DELETED
        account.save()
        messages.success(request, f"Account {mac_address} wurde gelöscht")
        return redirect(self.success_url)

class IotDeviceUpdate(IotDeviceBaseMixin, UpdateView):
    fields = []
    
    def form_valid(self, form):
        account = self.object
        account.password = generate_password()
        account.save()
        messages.success(
            self.request,
            f"{account.mac_address}|{account.password}|{account.device_name}",
            extra_tags='credentials'
        )
        return redirect('iotdevices:list')