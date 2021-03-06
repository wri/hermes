# Hermes - Messanger for the gods
# Copyright (C) 2014 World Resource Institute
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Module that supports admin emails for subscriptions."""

import email
import logging
import webapp2

from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

import model


_ADMINS = ['bguzder-williams@wri.org', 'cdavis@wri.org', 'ABarrett@wri.org',
           'tmaschler@wri.org','jmessinger@wri.org']


class AdminHandler(InboundMailHandler):
    """Handler for subscription requests by admin."""

    @classmethod
    def is_admin(cls, sender):
        """Return True if sender is an admin, otherwise return False."""
        name, mail = email.Utils.parseaddr(sender)
        if mail:    
            return mail.lower() in _ADMINS
        else:
            return False

    @classmethod
    def get_subscriptions(cls, body):
        """Return generator of subscription dictionaries from body."""
        for line in body.splitlines():
            if not line.strip():  # Skip any blank lines in body
                continue
            yield dict(zip(['name', 'mail', 'team', 'status', 'role'],
                       [x.strip() for x in line.split(',')]))

    @classmethod
    def update_subscription(cls, data):
        """Updates subscription model with supplied data or creates new one."""
        subscriber = model.Subscriber.get_or_insert(**data)
        subscriber.status = data.get('status', 'subscribe')
        subscriber.role = data.get('role')
        subscriber.put()

    @classmethod
    def get_subscription_report(cls, subscriptions):
        """Return text report from sequence of Subscription dictionaries."""
        return '\n'.join([u'{name} <{mail}> {team} {status} {role}'
               .format(**x)
               for x in subscriptions])

    @classmethod
    def get_subscription_msg(cls, to, report):
        """Returns EmailMessage for supplied recipient and report."""
        reply_to = 'Hermes <noreply@hermes-hub.appspotmail.com>'
        fields = dict(
            sender=reply_to,
            to=to,
            reply_to=reply_to,
            subject='[Hermes] Admin confirmation - Your changes were saved',
            body=report)
        return mail.EmailMessage(**fields)

    @classmethod
    def process_message(cls, sender, body):
        """Process subscription lines in body and send report to sender."""
        if not cls.is_admin(sender):
            logging.info('Ignoring admin request from non-admin %s' % sender)
            return
        map(cls.update_subscription, cls.get_subscriptions(body))
        report = cls.get_subscription_report(
            [x.to_dict() for x in model.Subscriber.query().iter()])
        cls.get_subscription_msg(sender, report).send()

    def receive(self, message):
        """Receive mail, create/update subscriptions, mail confirmation."""
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        self.process_message(message.sender, body)

routes = [
    AdminHandler.mapping(),
]

handlers = webapp2.WSGIApplication(routes, debug=True)
