from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import Event
from .forms import EventForm
from django.http import HttpResponse
from django.utils.text import slugify
from .utils import generate_event_pdf

class EventsRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perm('events.events_access')

class EventsBaseMixin(LoginRequiredMixin, EventsRequiredMixin):
    model = Event
    success_url = reverse_lazy('events:list')

    def get_queryset(self):
        return Event.objects.filter(creator=self.request.user).exclude(
            status=Event.Status.DELETED
        )

class EventListView(EventsBaseMixin, ListView):
    template_name = 'events/event_list.html'
    context_object_name = 'events'

class EventCreateView(EventsBaseMixin, CreateView):
    form_class = EventForm
    template_name = 'events/event_form.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        
        # Accounts generieren
        if self.object.generate_accounts():
            messages.success(self.request, f'{self.object.number} Accounts wurden erfolgreich generiert')
        else:
            messages.error(self.request, 'Accounts konnten nicht generiert werden')
            
        return response

class EventUpdateView(EventsBaseMixin, UpdateView):
    form_class = EventForm
    template_name = 'events/event_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Veranstaltung erfolgreich aktualisiert')
        return super().form_valid(form)

class EventDetailView(EventsBaseMixin, DetailView):
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guests'] = self.object.guests.all()
        return context
    
class EventPDFView(EventsBaseMixin, DetailView):
    def get(self, request, *args, **kwargs):
        event = self.get_object()
        
        # PDF generieren
        pdf = generate_event_pdf(event)
        
        # Als Download bereitstellen
        filename = f"zugangsdaten-{slugify(event.name)}.pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
class EventDeleteView(EventsBaseMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        event.delete()
        messages.success(request, f'Event {event.name} wurde gelöscht. Alle Zugangsdaten wurden deaktiviert')
        return redirect(self.success_url)