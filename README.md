# Debian 10 stack

This repo contains
Ansible playbooks and roles
that are meant to run in pull mode
to deploy a generally useful stack
on an IPv4/IPv6 Debian 10 host
that includes:

- Mailer config.
- Let's Encrypt certificates.
- Opinionated `iptables` and `ipset` configuration.
- A custom firewall API.
  that attempts to bridge the gap
  between IPv4 and IPv6 network stacks.


## Opinions

The stack and I are both quite opinionated,
though most of our opinions are open to change
if we feel it's not too painful to adapt.

### Debian 10

The stack is Debian 10 only
because its primary purpose
is to run FreeSWITCH,
and Debian 10 is the deployment platform
recommended by the FreeSWITCH project.

The stack may or may not
work just as well on Ubuntu.

### Email

The stack makes it simple,
but not mandatory,
to configure `exim4`
to send email via a third party SMTP service.
If you don't change the `mail_*` and `exim_*` vars,
all alerts go to the root account.

I like to use per-host Fastmail app passwords.
Gmail also lets you create app passwords,
but only when you enable
what Google calls 2-step verification,
and that requires giving Google a phone number,
which is never going to happen.

The `mail_admin_email` address
should not be in the same domain as the hostname
or alert emails will stay on the host.

### Let's Encrypt certificates

You must control a DNS domain
to deploy this stack,
and the host must be configured with
at least one public IPv4 address
and one public IPv6 address.
A and AAAA records must be configured
for the first of each type of address
found in the output of `hostname --all-ip-addresses`.

When A and AAAA records
are configured correctly for the host,
the nginx role generates Let's Encrypt certs automatically.

### Firewall

Hosts are configured
to allow access to the SSH port
from a single IPv4 address.
You should be very careful
when configuring the `firewall_admin_addr` var,
and you might want to use the firewall API
to implement some sort of port knocking
so you don't lock yourself out.

There are quite a few services out there
to check your public IPv4 address.

    https://ipecho.net/plain
    https://icanhazip.com/
    https://ifconfig.co/
    https://ifconfig.me/

### SSH

The stack has no opinion
on how to configure the SSH daemon,
but I do.
I like to configure hosts
to allow root login only,
and only by authorized key.
To do so,
configure only the following options
in `/etc/ssh/sshd_config`.

    PermitRootLogin yes
    ChallengeResponseAuthentication no
    UsePAM yes
    PasswordAuthentication no

### Python 3

Though Ansible itself
runs in a Python 3 venv,
Ansible runs modules
using the platform interpreter
unless the `ansible_python_interpreter` is specified.
Since I like to use Python 3 as much as possible
and this repo contains custom modules
that use Python 3 features,
and since according to the
[Ansible documentation](https://docs.ansible.com/ansible/latest/reference_appendices/python_3_support.html),
core modules should work fine in Python 3,
variables should point the interpreter var
at the platform's Python 3 interpreter.


# Setup

Run the following commands on the host as root
to install Ansible on the host in a Python 3 venv.

    mkdir -p /opt/ansible
    chmod 0700 /opt/ansible
    cd /opt/ansible
    apt update
    apt install git python3-venv python3-apt
    python3 -m venv venv

Run the following commands to upgrade pip and install Ansible.

    . venv/bin/activate
    pip install --upgrade pip
    pip install ansible


# Deployment

Copy the repo's `stack-vars.yml`
to `/opt/ansible/`
and modify it for the host.

Run the following command on the host
to have Ansible pull the repo
and run `local.yml` to deploy the stack.

    /opt/ansible/venv/bin/ansible-pull \
    -U https://github.com/tessercat/stack-deploy -i hosts \
    -e @/opt/ansible/stack-vars.yml


# Maintenance

Upgrade pip and Ansible
to keep the venv up to date.

    pip install --upgrade pip ansible

Run the `ansible-pull` command regularly,
possibly in a systemd timer,
to keep the stack up to date.


# Development


