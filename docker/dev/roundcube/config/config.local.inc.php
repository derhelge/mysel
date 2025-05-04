<?php
$config['oauth_provider']='generic';
$config['oauth_provider_name'] = 'SSO';
$config['oauth_client_id'] = 'roundcube';
$config['oauth_client_secret'] = getenv('ROUNDCUBEMAIL_OIDC_SECRET');
$config['oauth_auth_uri'] = "http://keycloak:8080/realms/example/protocol/openid-connect/auth";
$config['oauth_token_uri'] = "http://keycloak:8080/realms/example/protocol/openid-connect/token";
$config['oauth_identity_uri'] = "http://keycloak:8080/realms/example/protocol/openid-connect/userinfo";
$config['oauth_logout_uri'] = "http://keycloak:8080/realms/example/protocol/openid-connect/logout";
$config['oauth_verify_peer'] = false;
$config['oauth_scope'] = "email profile openid";
$config['oauth_auth_parameters'] = [];
$config['oauth_identity_fields'] = ['preferred_username'];
$config['oauth_login_redirect'] = false;

$config['imap_conn_options'] = array(
    'ssl' => array(
    'verify_peer' => false,
    'verify_peer_name' => false
    ),
);

#$config['plugins'] = array_filter(array_unique(array_merge($config['plugins'], ['oidc_logout'])));