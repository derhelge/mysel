FROM freeradius/freeradius-server:latest
COPY raddb/ /etc/raddb/
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
