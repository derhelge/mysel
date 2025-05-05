# apps/guests/views.py
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import ValidationError
from django.utils import timezone 
from django.db.models import Q

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from apps.guests.utils import send_guest_notification, send_owner_notification
from .models import GuestAccount
from .forms import GuestForm, GuestApplicationForm

class GuestRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perm('guests.sponsoring_access')

class GuestBaseMixin(LoginRequiredMixin, GuestRequiredMixin):
    model = GuestAccount
    success_url = reverse_lazy('guests:list')

    def get_queryset(self):
        return GuestAccount.objects.filter(owner=self.request.user)
    
class GuestAccountCreateView(GuestBaseMixin, CreateView):
    template_name = 'guests/guest_form.html'
    form_class = GuestForm

    def form_valid(self, form):
        guest = form.save(commit=False) 
        guest.owner = self.request.user
        try:
            guest.activate()
            messages.success(self.request, f'Gast {guest.name} wurde aktiviert.')
        except ValidationError as e:
            messages.error(self.request, e.messages[0])
        
        send_guest_notification(guest,'activate')

        messages.info(self.request, f"{guest.username}|{guest.password}", extra_tags='credentials')
        return redirect(self.success_url)
    
class GuestAccountApplicateView(CreateView):
    template_name = 'guests/guest_form.html'
    form_class = GuestApplicationForm

    def form_valid(self, form):
        guest = form.save(commit=False)
        owner_email = form.cleaned_data['owner_email']
        guest.create_pending_user(temp_owner_email=owner_email)
        send_guest_notification(guest, 'applicate')
        send_owner_notification(guest, owner_email)
        
        return render(self.request, 'guests/application_success.html', {'guest': guest})

class GuestAccountApproveView(GuestBaseMixin, View):
    def get(self, request, *args, **kwargs):
        guest = self.get_queryset().get(pk=self.kwargs['pk'])

        try:
            guest.activate()
            send_guest_notification(guest,'approve')
            messages.success(self.request, f'Gast {guest.name} wurde aktiviert.')
        except ValidationError as e:
            messages.error(self.request, e)
        
        return redirect(self.success_url)
    
class GuestAccountUpdateView(GuestBaseMixin, UpdateView):
    fields = ['duration']
    VALID_ACTIONS = {'activate', 'extend', 'reactivate'}

    def form_valid(self, form):
        guest = self.object
        action = self.request.POST.get('action')
        days = form.cleaned_data['duration']

        if action not in self.VALID_ACTIONS:
            raise ValueError('Ungültige Aktion')
        
        try:
            if action == 'activate':
                guest.activate(duration=days)
                messages.success(self.request, f'Gast {guest.name} wurde aktiviert.')
            elif action == 'extend':
                guest.extend(duration=days)
                messages.success(self.request, f'Gast {guest.name} wurde um {days} Tage verlängert.')
            elif action == 'reactivate':
                guest.reactivate(duration=days)
                messages.success(self.request, f'Gast {guest.name} wurde reaktiviert für {days} Tage.')
            
            send_guest_notification(guest, action)
            
        except Exception as e:
            messages.error(self.request, e)

        return redirect(self.success_url)

class GuestAccountDeleteView(GuestBaseMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        guest = self.get_object()
        guest.delete()
        messages.success(request, f'Gast-Account {guest.username} wurde gelöscht.')
        return redirect(self.success_url)

class GuestAccountListView(GuestBaseMixin, ListView):
    template_name = 'guests/guest_list.html'
    context_object_name = 'guests'
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_queryset = self.get_queryset()
        
        context.update({
            'pending_guests': base_queryset.filter(status=GuestAccount.Status.PENDING),
            'active_guests': base_queryset.filter(status=GuestAccount.Status.ACTIVE, end_date__gte=timezone.now()),
            'deleted_guests': base_queryset.filter(
                Q(end_date__range=(timezone.now() - timedelta(days=14),timezone.now()))
                | (
                    Q(status=GuestAccount.Status.DELETED,end_date__gte=timezone.now() - timedelta(days=14))
                  )
            ),
        })
        return context