# Email Authentication PoC

## Übersicht
Dieser Proof of Concept (PoC) demonstriert eine Authentifizierungslösung für E-Mail-Dienste, die sowohl OAuth2 für Webmail als auch gerätebasierte Authentifizierungen für native E-Mail-Clients (Thunderbird, etc.) unterstützt.

## Hauptfunktionen
- Webmail-Zugriff via OAuth2/OIDC
- Selfservice-Portal für Benutzer
 - Verwaltung von Geräte-spezifischen Passwörtern über Webinterface
- Automatische Deaktivierung der LDAP-Authentifizierung nach Einrichtung von Geräte-Passwörtern

## Komponenten
- OpenLDAP (Benutzerverwaltung)
- Keycloak (Identity Provider)
- PostgreSQL (Datenbank)
- Roundcube (Webmail-Client)
- Dovecot/Postfix (Mailserver)
- FreeRADIUS (für WLAN-Accounts)
- Django (Selfservice-Portal)

![Übersichtsdiagram](mysel.drawio.svg)

## Voraussetzungen
- Docker und Docker Compose
- OpenSSL (um die LDAP-Passwörter zu generieren)
- Bearbeitung der `/etc/hosts` Datei
- Browser auf dem Docker-Host-System

## Installation

### 1. Hosts-Einträge
Fügen Sie folgende Einträge in `/etc/hosts` hinzu:
```
127.0.0.1 myselfservice
127.0.0.1 keycloak
127.0.0.1 roundcube
```

### 2. Initialisierung
```bash
cd docker/dev
./init.sh
```

Das `init.sh` Script automatisiert die initiale Einrichtung:

- Erstellt eine `.env` Datei aus der `env.example`
- ruft ein Script `openldap/generate_bootstrap.sh` auf um OpenLDAP zu vorzubereiten

### 3. Start des Systems und Nutzung
```bash
docker compose -f docker-compose.dev.yml up --build
```
1. Initialzustand:
    - Anmeldung an Webmail http://roundcube:8081 (SSO) und LDAP-Zugangsdaten (Username: testuser1@example.org, Passwort: testuser1)
    - Gültige Anmeldung an imap (localhost:143 STARTTLS) mit LDAP-Zugangsdaten
2. Wechsel zu Geräte-Passwörtern:
    1. Anmelden an Django-Webinterface (SSO (Username: testuser1@example.org, Passwort: testuser1)) -> Email-Konten -> Account generieren
    2. Anmeldung mit LDAP-Zugangsdaten an imap (localhost:143 STARTTLS) nicht mehr möglich
    3. Anmeldung nur noch mit generierten Zugangsdaten möglich

Dieser Testablauf wird beim Start von `docker compose -f docker-compose.dev.yml up --build` automatisch mit dem User `testuser2@example.org` im Container tests durchgeführt. 


## Neustart nach Konfigurationsänderungen
Bei Änderungen an der Konfiguration:
```bash
docker compose -f docker-compose.dev.yml down --volumes
docker compose -f docker-compose.dev.yml up --build
```

## Hinweis
Alle Docker Volumes müssen entfernt werden (`docker compose down --volumes`), wenn Konfigurationsänderungen vorgenommen wurden, da sich einige Services sonst nicht korrekt neu initialisieren.
