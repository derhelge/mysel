FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
    supervisor \
    ca-certificates \
    dovecot-core \
    dovecot-ldap \
    dovecot-pgsql \
    dovecot-lmtpd \
    dovecot-imapd \
    postfix \
    postfix-ldap \
    postfix-pgsql \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 5000 vmail \
    && useradd -m -d /var/vmail -s /bin/false -u 5000 -g vmail vmail \
    && chown vmail:vmail /var/vmail/

VOLUME ["/var/mail"]

RUN mkdir -p /var/spool/postfix/private \
    && chown -R postfix:postfix /var/spool/postfix/ \
    && chmod -R 0700 /var/spool/postfix/private/

COPY main.cf /etc/postfix/
COPY master.cf /etc/postfix/
COPY virtual.ldap /etc/postfix/
COPY relay_domains /etc/postfix/

RUN postmap /etc/postfix/relay_domains

COPY dovecot.conf /etc/dovecot/
COPY dovecot-ldap.conf.ext.template /etc/dovecot/
COPY dovecot-sql.conf.ext.template /etc/dovecot/
COPY dovecot-oauth2.conf.ext /etc/dovecot/

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 25 143 465 993 995

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

