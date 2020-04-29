# Debian stack

This repo contains
Ansible playbooks and roles
to deploy a generally useful stack
on a Debian-based host
that includes:

- Exim mailer config.
- Nginx and Let's Encrypt certificates.
- Opinionated `iptables` and `ipset` configuration.
- A simple localhost firewall API.
- Basic prometheus node and firewall metrics/alerts.

You must control a DNS domain
to deploy this stack.
Configure A and AAAA records for the host,
and when DNS records are configured correctly,
the nginx role generates Let's Encrypt certs automatically.


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

**Firewall**

The firewall is simple ipset and iptables configuration
and a very simple HTTP API.

The firewall API lets localhost services:

- Port knock the SSH port
  by adding addresses to `admin4` and `admin6` ipsets.
- Open/close other ports and ranges of ports
  by adding/deleting iptables INPUT ACCEPT rules.

**Custom ipset address lists**

The ipset service
loads addresses into ipsets
from files in `/opt/firewall/ipset/lists/`.

When the `ssh_admin_only` stack var is `true`,
iptables drops all traffic to the SSH port
except from addresses in `admin4` and `admin6` sets.

All traffic from addresses in `block4` and `block6` sets
is dropped.

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

You might also use the firewall API
to implement port knocking.
The `firewall-app` repo
does so for Django projects
on admin login.
