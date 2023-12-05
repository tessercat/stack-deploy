""" Ansible module to run the certbot script. """
import os
from pathlib import Path
import subprocess
from subprocess import PIPE
from ansible.module_utils.basic import AnsibleModule


def _run_certbot(fstring, domain):
    """ Run certbot for a domain.

    Certbot is a Python library, but it seems to have been designed to be
    used only via cli, not as an API. Use subprocess.
    """
    # Check cert path.

    path = Path('/etc/letsencrypt/live') / domain
    if os.path.exists(path):
        return False

    with subprocess.Popen(
        fstring % domain,
        stderr=PIPE,
        stdout=PIPE,
        shell=True
    ) as popen:
        _, err = popen.communicate()

    # Check cert path or raise.
    if os.path.exists(path):
        return True
    raise AssertionError(err)


def _run_module(admin_email, hostname, other_hostnames):
    """ Run the certbot command separately for each hostname. """
    # args = '--nginx --agree-tos -n --test-cert'
    args = '--nginx --agree-tos -n'
    fstring = f'certbot certonly {args} -m {admin_email} -d %s'
    changed = []
    changed.append(_run_certbot(fstring, hostname))
    for domain in other_hostnames:
        changed.append(_run_certbot(fstring, domain))
    return any(changed)


def run_module():
    """ Init and run module. """
    module_args = {
        'admin_email': {'type': 'str', 'required': True},
        'hostname': {'type': 'str', 'required': True},
        'other_hostnames': {'type': 'list', 'required': True}
    }
    module = AnsibleModule(
        argument_spec=module_args,
    )
    exit_json = {
        'changed': False,
        'failed': False,
        'failure': None
    }
    try:
        exit_json['changed'] = _run_module(
            module.params['admin_email'],
            module.params['hostname'],
            module.params['other_hostnames'],
        )
    except (OSError, AssertionError) as err:
        exit_json['failed'] = True
        exit_json['failure'] = repr(err)
    module.exit_json(**exit_json)


def main():
    """ Run the module. """
    run_module()


if __name__ == '__main__':
    main()
