import requests
import certifi
import logging
from django.conf import settings
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class FirewallAPIError(Exception):
    """Exception für Firewall API Fehler"""
    pass

class FakeFirewallService:
    _rule_states: Dict[str, bool] = {}

    def get_rule_status(self, uuid: str) -> bool:
        """Gibt den gefakten Status einer Regel zurück (Default: False)"""
        return self._rule_states.get(uuid, False)
    
    def toggle_rule(self, uuid: str, enabled: bool) -> Tuple[bool, str]:
        """Speichert den neuen Status und gibt Erfolg zurück"""
        self._rule_states[uuid] = enabled
        action = "Enabled" if enabled else "Disabled"
        return True, action

class RealFirewallService:
    def __init__(self):
        self.api_key = getattr(settings, 'FIREWALL_API_KEY', None)
        self.api_secret = getattr(settings, 'FIREWALL_API_SECRET', None)
        self.remote_uri = getattr(settings, 'FIREWALL_REMOTE_URI', None)
        
        if not all([self.api_key, self.api_secret, self.remote_uri]):
            raise FirewallAPIError(
                "Firewall API Konfiguration unvollständig. "
                "FIREWALL_API_KEY, FIREWALL_API_SECRET und FIREWALL_REMOTE_URI müssen gesetzt sein."
            )
    
    def get_rule_status(self, uuid: str) -> bool:
        try:
            response = requests.get(
                f"{self.remote_uri}/api/firewall/filter/get_rule/{uuid}",
                auth=(self.api_key, self.api_secret),
                verify=certifi.where(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('rule', {}).get('enabled') == "1"
            
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"Fehler beim Abrufen der Firewall-Regel {uuid}: {e}")
            raise FirewallAPIError(f"API-Fehler: {e}")
    
    def toggle_rule(self, uuid: str, enabled: bool) -> Tuple[bool, str]:
        try:
            enabled_param = "1" if enabled else "0"
            response = requests.post(
                f"{self.remote_uri}/api/firewall/filter/toggle_rule/{uuid}?enabled={enabled_param}",
                auth=(self.api_key, self.api_secret),
                verify=certifi.where(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            success = (
                (enabled and data.get('result') == 'Enabled') or
                (not enabled and data.get('result') == 'Disabled')
            )
            
            action = "eingeschaltet" if enabled else "ausgeschaltet"
            message = f"Regel erfolgreich {action}" if success else f"Fehler beim {action.replace('t', 'ten')} der Regel"
            
            return success, message
            
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"Fehler beim Umschalten der Firewall-Regel {uuid}: {e}")
            return False, f"API-Fehler: {e}"


def FirewallService():
    """Factory Funktion für Firewall Service - nutzt Fake in DEV, Real in PROD"""
    use_fake = getattr(settings, 'USE_FAKE_FIREWALL', settings.DEBUG)
    
    if use_fake:
        logger.info("Verwende FakeFirewallService für Development")
        return FakeFirewallService()
    else:
        logger.info("Verwende RealFirewallService für Production")
        return RealFirewallService()