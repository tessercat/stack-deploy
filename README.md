# Debian stack

This repo contains
Ansible playbooks and roles
to deploy a generally useful stack
on a Debian-based host
that includes:

- Exim mailer config.
- Nginx and Let's Encrypt certificates.
- Opinionated `iptables` and `ipset` configuration
  and a localhost-only firewall service to manage it.
- Prometheus node metrics/alerts.

You must control a DNS domain
to deploy this stack.
Configure A and AAAA records for the host,
and when DNS records are configured correctly,
the `certbot` role generates Let's Encrypt certs automatically.


## Other stack repos

- [firewall-service](https://github.com/tessercat/firewall-service) An HTTP service to manage ipset entries on localhost.
- [firewall-config](https://github.com/tessercat/firewall-config) Netfilter plugins and config data for a simple ipset-based iptables firewall.


## Stack vars

**Email**

The stack makes it simple,
but not mandatory,
to configure `exim4`
to send email via a third party SMTP service.
When configured correctly,
services running on the host
can send email to off-host addresses
by sending mail to `localhost:25`.

A callback plugin
mails playbook reports
to the `admin_email` stack var.

The `admin_email` domain
must be different from `hostname`
or mail stays on the host.

**Certificates**

The stack runs Let's Encrypt `certbot`
for the `hostname` domain
and for each domain listed in `other_hostnames`,
and does not modify nginx server config.

The stack configures nginx servers
for hostnames in `parked_domains`
to serve a slightly branded index page
that simply links to `mailto:postmaster@<domain>`.
The list should include domains
in `hostname` and `other_hostnames`
whose nginx config
is not installed
by other means.

Remove a domain's `/etc/letsencrypt/live` directory
and its `/etc/nginx/conf.d` file
by hand when removing hostname domains.

The stack installs a certbot hook script
that mails the host admin
when certificates change.

**Firewall**

The firewall is `netfilter-persistent` modules,
`ipset` and `iptables` configuration
and a very simple HTTP API
to allow localhost services
to add addresses to ipsets.

**Custom ipset address lists**

The `netfilter-persistent` modules
initialize ipsets and iptables rules
from files in subdirectories of `/opt/firewall/config/`.
See the stack's `config` role for more information.

When the `ssh_admin_only` stack var is `true`,
iptables drops all traffic to the SSH port
except from addresses in `admin.v4` and `admin.v6` lists.

**SSH access**

When the `ssh_admin_only` stack var is `false` (the default),
the SSH port is open to the world.
Set it to `true`
to block access to the SSH port
to all but addresses in admin ipsets.

If you restrict access to the SSH port,
you should place a public IP address
in one of the admin address lists
or you'll lock yourself out
of future connections.

You might also use the firewall service
to implement port knocking
of some kind.

**Monitored services**

The `monitored_services` stack var
is the list of `systemd` service names
that must be active.

Prometheus/alertmanager emails the host admin
when any of the listed services are down.


## Prometheus and Alertmanager access

To view prometheus/alertmanager web apps,
add location statements to `{{ hostname }}` nginx config by hand
in `/etc/nginx/conf.d`.

    location /metrics/prometheus/ {
        proxy_pass http://localhost:9090;
    }
    location /metrics/alertmanager/ {
        proxy_pass http://localhost:9093;
    }


## Stack-deploy service

The `service` role
disables apt-daily services,
removes the `unattended-upgrades` package,
and installs service and timer files
that run the `stack-deploy` playbook
automatically once per day in the early morning.
