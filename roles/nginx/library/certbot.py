""" Ansible module to run the certbot script. """
import os
import subprocess
from subprocess import PIPE
from ansible.module_utils.basic import AnsibleModule


def _certbot(webroot, admin_email, hostname, other_hostnames):
    """ Run the certbot command (webroot plugin) to obtain a cert.

    Certbot is a Python library, but it seems to have been designed to be
    used only via cli, not as an API. Use subprocess.
    """

    # Check that the cert for the host doesn't already exist.
    path = os.path.join('/etc/letsencrypt/live', hostname)
    if os.path.exists(path):
        return False

    # Expect one hostname and a space-delimited set of other hostnames.
    hosts = [hostname] + other_hostnames.split()

    # Run the certbot command.
    cmd = 'certbot certonly --agree-tos --webroot -n -m %s -w %s %s'
    hostparms = '-d %s' % ' -d '.join(hosts)
    cmd = cmd % (admin_email, webroot, hostparms)
    popen = subprocess.Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
    _, err = popen.communicate()

    # Check that the cert exists.
    if os.path.exists(path):
        return True
    raise AssertionError(err)


def main():
    """ Init and run module. """
    module = AnsibleModule(argument_spec={
        'webroot': {'required': True},
        'admin_email': {'required': True},
        'hostname': {'required': True},
        'other_hostnames': {'required': True},  # Space delimited.
    })
    exit_json = {
        'changed': False,
        'failed': False,
        'failure': None
    }
    try:
        exit_json['changed'] = _certbot(
            module.params['webroot'],
            module.params['admin_email'],
            module.params['hostname'],
            module.params['other_hostnames'],
        )
    except (OSError, AssertionError) as err:
        exit_json['failed'] = True
        exit_json['failure'] = repr(err)
    module.exit_json(**exit_json)


if __name__ == '__main__':
    main()
