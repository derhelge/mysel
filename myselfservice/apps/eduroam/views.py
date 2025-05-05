from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from .models import EduroamAccount
from .forms import EduroamAccountForm
from apps.core.utils import generate_password

class EduroamRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perm('eduroam.eduroam_access')

class EduroamBaseMixin(LoginRequiredMixin, EduroamRequiredMixin):
    model = EduroamAccount
    success_url = reverse_lazy('eduroam:list')

    def get_queryset(self):
        return EduroamAccount.objects.filter(
            owner=self.request.user,
            status=EduroamAccount.Status.ACTIVE
        )

class EduroamList(EduroamBaseMixin, ListView):
    template_name = 'eduroam/eduroam_list.html'
    context_object_name = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EduroamAccountForm()
        return context

class EduroamCreate(EduroamBaseMixin, CreateView):
    form_class = EduroamAccountForm

    def form_valid(self, form):
        if not EduroamAccount.check_account_limit(self.request.user):
            messages.error(
                self.request,
                f'Limit von {settings.EDUROAM_SETTINGS["MAX_ACCOUNTS"]} Accounts erreicht!'
            )
            return redirect(self.success_url)

        account = form.save(commit=False)
        account.owner = self.request.user
        #account.username wird über signal generiert
        account.password=generate_password()
        account.save()
        
        messages.info(
            self.request, 
            f"{account.username}|{account.password}",
            extra_tags='credentials'
        )
        return redirect(self.success_url)

class EduroamDetail(EduroamBaseMixin, DetailView):
    def get(self, request, *args, **kwargs):
        account = self.get_object()
        messages.info(
            request, 
            f"{account.username}|{account.password}",
            extra_tags='credentials'
        )
        return redirect('eduroam:list')
    
class EduroamDelete(EduroamBaseMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        account = self.get_object()
        username = account.username
        account.status = EduroamAccount.Status.DELETED
        account.save()
        messages.success(request, f"Account {username} wurde gelöscht")
        return redirect(self.success_url)

class EduroamUpdate(EduroamBaseMixin, UpdateView):
    fields = []
    
    def form_valid(self, form):
        account = self.object
        account.password = generate_password()
        account.save()
        messages.success(
            self.request,
            f"{account.username}|{account.password}",
            extra_tags='credentials'
        )
        return redirect('eduroam:list')