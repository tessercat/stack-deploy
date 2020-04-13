This role

- Configures default nginx servers.
- Configures the certbot webroot path.
- Runs certbot when Let's Encrypt certificates are missing.
- Configures a certbot post-renewal hook
  that restarts nginx when certs are renewed.

Default nginx servers
listen on ports 80 and 443
of all IPv4 and IPv6 public addresses.
Both servers return 444,
and the role does not configure
domain-specific servers,
so nginx drops all HTTP and HTTPS traffic
unless other roles add them.

To run certbot,
handler tasks archive existing
nginx server config
and replace it with config
that accepts all requests to the
`letsencrypt_webroot` stack var.
Handler tasks then run certbot
in a custom Ansible module
and restore the original server config.

Other roles *must* configure
nginx servers on port 80
that serve the certbot-generated files
in `letsencrypt_webroot`
for specific domains.

    server {
        listen 80;
        listen [::]:80;
        server_name {{ hostname }};
        location /.well-known {
            root {{ letsencrypt_webroot }};
        }
        location / {
            return 301 https://{{ hostname }}$request_uri;
        }
    }
