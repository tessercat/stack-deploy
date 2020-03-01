# Copyright 2020 Peter Christensen. All rights reserved.
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from email.message import EmailMessage
import smtplib
from pprint import pformat
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """ Send failed and changed task and playbook stats events
    to the inventory API port and email host admin on error. """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'event'
    CALLBACK_NEEDS_WHITELIST = False

    _play = None

    def _email_admin(self, subject, body):
        """ Email host admin. """
        msg = EmailMessage()
        msg.set_content(body)
        play_vars = self._play.get_variable_manager().get_vars()
        msg['Subject'] = '[%s] %s' % (play_vars['hostname'], subject)
        msg['From'] = '<noreply@%s>' % play_vars['hostname']
        msg['To'] = '<%s>' % play_vars['admin_email']
        with smtplib.SMTP('localhost') as server:
            server.send_message(msg)

    # Callback overrides.

    def playbook_on_stats(self, stats):
        """ Process playbook stats event for each host. """
        data = {}
        for host in stats.processed.keys():
            data[host] = stats.summarize(host)
            status = 'complete'
            if data[host]['failures'] or data[host]['unreachable']:
                status = 'failed'
        self._email_admin('%s %s' % (self._play.name, status), pformat(data))

    def runner_on_failed(self, host, res, ignore_errors=False):
        """ Process failed task result. """
        self._email_admin('Task failed', pformat(res))

    def v2_playbook_on_play_start(self, play):
        """ Process playbook start events. """
        self._play = play
