from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, View
from django.http import JsonResponse

from .models import FirewallRule, FirewallRuleChange
from .services import FirewallService, FirewallAPIError

import logging

logger = logging.getLogger(__name__)
class FwConfigRequiredMixin(UserPassesTestMixin):
    """Mixin zur Überprüfung der FwConfig-Berechtigung"""
    def test_func(self):
        return self.request.user.has_perm('fwconfig.fwconfig_access')

class FwConfigBaseMixin(LoginRequiredMixin, FwConfigRequiredMixin):
    """Basis-Mixin für alle FwConfig Views"""
    success_url = reverse_lazy('fwconfig:list')

class FwConfigListView(FwConfigBaseMixin, ListView):
    """Hauptansicht mit Firewall-Regeln und Änderungshistorie"""
    template_name = 'fwconfig/fwconfig_list.html'
    context_object_name = 'firewall_rules'
    
    def get_queryset(self):
        return FirewallRule.objects.filter(is_active=True).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_changes'] = FirewallRuleChange.objects.select_related(
            'firewall_rule', 'user'
        )[:10]
        
        service = FirewallService()
        
        for rule in context['firewall_rules']:
            try:
                rule_status = service.get_rule_status(str(rule.uuid))
                rule.remote_rule_status = rule_status
                rule.save(update_fields=['remote_rule_status'])
                logger.debug(f"Status der Regel {rule.uuid}: {rule_status}")
            except FirewallAPIError:
                rule.remote_rule_status = False
                rule.save(update_fields=['remote_rule_status'])
                
        return context

class FwConfigToggleView(FwConfigBaseMixin, View):
    """View zum Umschalten einer Firewall-Regel"""
    
    def post(self, request, pk):
        firewall_rule = get_object_or_404(FirewallRule, pk=pk, is_active=True)
        service = FirewallService()
        
        try:
            current_status = service.get_rule_status(str(firewall_rule.uuid))
            logger.debug(f"Aktueller Status der Regel {firewall_rule.uuid}: {current_status}")
            success, message = service.toggle_rule(str(firewall_rule.uuid), not current_status)
            
            if success:
                # Änderung protokollieren
                FirewallRuleChange.objects.create(
                    firewall_rule=firewall_rule,
                    user=request.user,
                    action='enabled' if not current_status else 'disabled',
                    api_success=True,
                    api_message=message
                )
                
                action_text = 'eingeschaltet' if not current_status else 'ausgeschaltet'
                messages.success(
                    request,
                    f'Firewall-Regel "{firewall_rule.name}" wurde erfolgreich {action_text}.'
                )
            else:
                # Fehler protokollieren
                FirewallRuleChange.objects.create(
                    firewall_rule=firewall_rule,
                    user=request.user,
                    action='enabled' if not current_status else 'disabled',
                    api_success=False,
                    api_message=message
                )
                
                messages.error(request, f'Fehler: {message}')
                
        except FirewallAPIError as e:
            messages.error(request, f'API-Fehler: {e}')
        
        return redirect(self.success_url)

class FwConfigStatusAPIView(FwConfigBaseMixin, View):
    """API-View für AJAX-Status-Updates"""
    
    def get(self, request, pk):
        firewall_rule = get_object_or_404(FirewallRule, pk=pk, is_active=True)
        service = FirewallService()
        
        try:
            is_enabled = service.get_rule_status(str(firewall_rule.uuid))
            return JsonResponse({
                'status': is_enabled,
                'name': firewall_rule.name,
                'error': None
            })
        except FirewallAPIError as e:
            return JsonResponse({
                'status': None,
                'name': firewall_rule.name,
                'error': str(e)
            })
