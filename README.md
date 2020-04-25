# Debian stack

This repo contains
Ansible playbooks and roles
to deploy a generally useful stack
on an IPv4/IPv6 Debian-based host
that includes:

- Mailer config.
- Let's Encrypt certificates.
- Opinionated `iptables` and `ipset` configuration.
- A simple custom firewall API
  to bridge the gap
  between IPv4 and IPv6 network stacks.


Ipset and iptables roles
assume a dual network stack
with at least one public IPv4 address
and one public IPv6 address.

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
If you don't change the `admin_email` and `smtp_*` vars,
all admin email goes to the `mail` account at `/var/mail/mail`.

The `admin_email` address
should not be in the same domain as the hostname
or alert emails will stay on the host.

**Firewall**

The firewall is ipset and iptables configuration
and a simple HTTP API.

The HTTP API lets localhost processes
port knock the SSH port
by adding addresses to admin whitelist ipsets,
and it lets processes
open and close other ports and ranges of ports
by adding/deleting iptables INPUT ACCEPT rules.

If you change any of the ipset lists in `/opt/firewall/ipset/lists`
after installing the stack,
restart ipset and firewall services.

    systemctl restart ipset.service firewall.service

**Admin whitelist**

By default, the SSH port is open to the world,
but the firewall can be configured
to disallow access to the (stack-vars-configurable) SSH port
from all but whitelisted IP addresses
by setting the `admin_whitelist` variable to `true`.

If you enable the `admin_whitelist` stack var,
you *must* whitelist your public IP address
or you *will* lock yourself out
of future connections
when the ipset service runs.

Add whitelisted addresses or CIDR subnets
(one address/subnet per line)
to `/opt/firewall/ipset/lists/whitelist4`
or `/opt/firewall/ipset/lists/whitelist6`.

You should also use the firewall API
to implement some sort of port knocking
in case your public IP address changes.
The `firewall-app` repo
can be used to do so for Django projects.

**Blacklist**

The iptables firewall rules
drop addresses and subnets
in ipsets loaded from files at
`/opt/firewall/ipset/lists/blacklist4`
and `/opt/firewall/ipset/lists/blacklist6`.
The `admin_whitelist` variable
doesn't have to be enabled to do so.
