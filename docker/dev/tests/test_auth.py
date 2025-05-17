import pytest
import requests
from bs4 import BeautifulSoup
import imaplib
import subprocess
import os
import re
import socket

class BaseKeycloakTest:
    def setup_method(self):
        self.base_url = "http://myselfservice:8000"
        self.keycloak_url = "http://keycloak:8080"
        self.session = requests.Session()
        self._login()

    def _login(self):
        # 1. Get login page 
        response = self.session.get(
            f"{self.base_url}/accounts/oidc/keycloak/login/",
            allow_redirects=False
        )
        
        # 2. Follow redirect to Keycloak
        keycloak_url = response.headers['Location']
        response = self.session.get(keycloak_url, allow_redirects=True)
        
        # 3. Extract form data
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', id='kc-form-login')
        
        hidden_inputs = {
            hidden.get('name'): hidden.get('value') 
            for hidden in form.find_all("input", type="hidden")
        }
        
        # 4. Submit login
        response = self.session.post(
            form.get('action'),
            data={
                'username': self.test_username,
                'password': self.test_password,
                **hidden_inputs
            },
            headers={
                'Origin': self.keycloak_url,
                'Referer': keycloak_url
            },
            allow_redirects=True
        )
        
        # Verify login successful
        response = self.session.get(f"{self.base_url}/{self.verify_path}")
        assert response.status_code == 200

    def _extract_credentials(self, response):
        username = re.search(r"modalUsername'\).value\s*=\s*[\"']([^\"']+)[\"']", response.text).group(1)
        password = re.search(r"modalPassword'\).value\s*=\s*[\"']([^\"']+)[\"']", response.text).group(1)
        return username, password

    def _get_csrf_and_post(self, path):
        response = self.session.get(f"{self.base_url}/{path}")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        return self.session.post(
            f"{self.base_url}/{path}/create/",
            data={'csrfmiddlewaretoken': csrf_token},
            headers={'Referer': f"{self.base_url}/{path}/create"},
            allow_redirects=True
        )

# class TestMailLogin(BaseKeycloakTest):
#     def setup_method(self):
#         self.mailserver = "mailserver" 
#         self.test_username = "testuser2@example.org"
#         self.test_password = "testuser2"
#         self.verify_path = "emaildevice"
#         super().setup_method()

#     def test_initial_imap_login(self):
#         imap = imaplib.IMAP4(host=self.mailserver, port=143)
#         imap.starttls()
#         imap.login(self.test_username, self.test_password)
#         imap.logout()

#     def test_create_email_device(self):
#         response = self._get_csrf_and_post('emaildevice')
#         username, password = self._extract_credentials(response)
        
#         # Test old credentials fail
#         with pytest.raises(imaplib.IMAP4.error):
#             imap = imaplib.IMAP4(self.mailserver)
#             imap.starttls()
#             imap.login(self.test_username, self.test_password)
            
#         # Test new credentials work
#         imap = imaplib.IMAP4(self.mailserver)
#         imap.starttls() 
#         imap.login(username, password)
#         imap.logout()

# import socket

class TestEduroamAccount(BaseKeycloakTest):
    def setup_method(self):
        self.test_username = "testuser3@example.org"
        self.test_password = "testuser3"
        self.verify_path = "eduroam"
        super().setup_method()

    def test_eduroam_account_creation(self):
        response = self._get_csrf_and_post('eduroam')
        username, password = self._extract_credentials(response)

        # Test radius
        result = subprocess.run(
            f"radtest {username} {password} freeradius 0 testing123",
            shell=True, capture_output=True, text=True
        )
        assert result.returncode == 0

        # Test eapol
        config = f"""network={{
            key_mgmt=IEEE8021X
            eap=TTLS
            identity="{username}"
            anonymous_identity="anonymous"
            password="{password}"
            ca_cert="/radius_certs/ca.pem"
            phase2="auth=PAP"
        }}"""
        
        with open("temp_eapol.conf", "w") as f:
            f.write(config)
        radius_ip = socket.gethostbyname('freeradius')

        result = subprocess.run(
            f"eapol_test -c temp_eapol.conf -s testing123 -a {radius_ip}",
            shell=True, capture_output=True, text=True
        )
        os.remove("temp_eapol.conf")
        assert result.returncode == 0

class TestRadiusClientAuth:
    def test_radius_auth(self):
        # Decrypt key first
        subprocess.run(
            "openssl rsa -in /radius_certs/client.key -out /client_unencrypted.key -passin pass:whatever",
            shell=True, check=True
        )

        config = f"""network={{
            key_mgmt=IEEE8021X
            eap=TLS
            identity="test_client"
            ca_cert="/radius_certs/ca.pem"
            client_cert="/radius_certs/client.pem" 
            private_key="/client_unencrypted.key"
        }}"""
        
        with open("temp_eapol.conf", "w") as f:
            f.write(config)
        radius_ip = socket.gethostbyname('freeradius')

        result = subprocess.run(
            f"eapol_test -c temp_eapol.conf -s testing1234 -a {radius_ip}",
            shell=True, capture_output=True, text=True
        )
        os.remove("temp_eapol.conf")
        os.remove("/client_unencrypted.key")
        assert result.returncode == 0