# apps/core/views.py
from django.views.generic import TemplateView
from django.contrib import auth
from django.shortcuts import redirect
from django.conf import settings
from allauth.account.views import LogoutView

class HomeView(TemplateView):
    template_name = 'core/home.html'
    def get_template_names(self):
        if not self.request.user.is_authenticated:
            return ['core/landing.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sso_provider'] = settings.SSO_PROVIDER
        return context

# leider hat allauth kein id_token, daher nur keycloak form-logout
# https://codeberg.org/allauth/django-allauth/issues/3694
class CustomLogoutView(LogoutView):
    def get(self, *args, **kwargs):

        # django logout
        auth.logout(self.request)
        
        # keycloak logout
        return redirect(settings.CUSTOM_LOGOUT_OIDC)