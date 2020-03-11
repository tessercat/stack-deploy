# Debian 10 stack

This repo contains
Ansible playbooks and roles
to deploy a generally useful stack
on an IPv4/IPv6 Debian 10 host
that includes:

- Mailer config.
- Let's Encrypt certificates.
- Opinionated `iptables` and `ipset` configuration.
- A simple custom firewall API
  to bridge the gap
  between IPv4 and IPv6 network stacks.


## Stack host

### Debian 10

The stack is Debian 10 only
because its primary purpose
is to run FreeSWITCH,
and Debian 10 is the deployment platform
recommended by the FreeSWITCH project.
The stack will probably work just as well on Ubuntu,
though my pre-compiled FreeSWITCH binaries
eventually won't run
due to updates to shared libraries
that FreeSWITCH depends on.

### Dual IPv4/IPv6 network stack

The playbook assumes that the host is configured with
at least one IPv4 address and one IPv6 address.

### Let's Encrypt certificates

You must control a DNS domain
to deploy this stack.
Configure A and AAAA records for the host,
and when DNS records are configured correctly,
the nginx role generates Let's Encrypt certs automatically.

### SSH daemon

The stack has no opinion
on how to configure the SSH daemon,
but I like to configure hosts
to allow root login only,
and only by authorized key.
To do so,
configure only the following options
in `/etc/ssh/sshd_config`.

    PermitRootLogin yes
    ChallengeResponseAuthentication no
    UsePAM yes
    PasswordAuthentication no


## Ansible environment

Run the following commands
as root on the Debian 10 host
to install Ansible on the host in a Python 3 venv.

    mkdir -p /opt/ansible
    chmod 0700 /opt/ansible
    cd /opt/ansible
    apt -y update
    apt -y install git python3-venv python3-apt
    python3 -m venv venv

Run the following commands
to upgrade pip and install Ansible
in the venv.

    . venv/bin/activate
    pip install --upgrade pip
    pip install ansible


## Stack vars

Copy the repo's `stack-vars.yml`
to `/opt/ansible/`.

    wget https://raw.githubusercontent.com/tessercat/stack-deploy/master/stack-vars.yml

Read the comments,
and modify the file for the host.

### Email

The stack makes it simple,
but not mandatory,
to configure `exim4`
to send email via a third party SMTP service.
If you don't change the `admin_email` and `smtp_*` vars,
all admin email goes to the `mail` account at `/var/mail/mail`.

The `admin_email` address
should not be in the same domain as the hostname
or alert emails will stay on the host.

### Firewall

If you change any of the lists
after installing the stack,
reload ipset and firewall services.

    systemctl reload ipset.service
    systemctl reload firewall.service

**Admin whitelist**

By default, the SSH port is open to the world,
but the firewall can be configured
to disallow access to the (stack-vars-configurable) SSH port
from all but whitelisted IP addresses
by setting the `admin_whitelist` variable to `true`.

If you enable the `admin_whitelist` stack var,
you must add whitelisted IP addresses
(or CIDR subnets)
to the files at
`/opt/ipset/lists/whitelist4`
or `/opt/ipset/lists/whitelist6`
(one address/subnet per line)
or you *will* lock yourself out
of future connections
when the ipset service runs.

You should also use the firewall API
to implement some sort of port knocking
in case your public IP address changes.

**Blacklist**

The iptables firewall
blacklists addresses and subnets
in files at
`/opt/ipset/lists/blacklist4`
and `/opt/ipset/lists/blacklist6`.
The `admin_whitelist` variable
doesn't have to be enabled to do so.


## Installation

Run the following command on the host
to deploy the stack.

    /opt/ansible/venv/bin/ansible-pull \
    -U https://github.com/tessercat/stack-deploy -i hosts \
    -e @/opt/ansible/stack-vars.yml


## Maintenance

Upgrade pip and Ansible
to keep the venv up to date.

    pip install --upgrade pip ansible

Run the `ansible-pull` command regularly,
possibly in a systemd timer,
to keep the stack up to date.


## Development

Run the following command on the host
to have Ansible pull the repo
and run `dev.yml` to set up for dev as root.

    /opt/ansible/venv/bin/ansible-pull dev.yml \
    -U https://github.com/tessercat/stack-deploy -i hosts \
    -e @/opt/ansible/stack-vars.yml
