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

import email
import webapp2
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import model
import time
import logging


_ADMINS = ['asteele@wri.org', 'cdavis@wri.org']


class AdminHandler(InboundMailHandler):
    """Handler for subscription requests by admin."""

    def update(self, data):
        """Updates subscription model for supplied data"""
        key_id = data['mail'].lower().strip()
        subscriber = ndb.Key(model.Subscriber, key_id).get()
        if not subscriber:
            subscriber = model.Subscriber(id=key_id, **data)
        else:
            subscriber.status = data.get('status', 'subscribe')
            subscriber.role = data.get('role')
        subscriber.put()

    def send_confirmation(self, to):
        """Sends confirmation email to with current state of subscriptions."""
        lines = [u'{name} <{mail}> status={status} role={role}'.format(**x.to_dict())
                 for x in model.Subscriber.query().iter()]
        reply_to = 'Hermes <noreply@hermes-hub.appspotmail.com>'
        mail.send_mail(
            sender=reply_to,
            to=to,
            reply_to=reply_to,
            subject='[Hermes] Admin confirmation',
            body="""Your changes were saved:\n\n%s""" % '\n'.join(lines))

    def receive(self, message):
        name, mail = email.Utils.parseaddr(message.sender)
        if not mail in _ADMINS:
            return
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        logging.info('ADMIN: body=%s' % body)
        for line in body.splitlines():
            data = dict(zip(['name', 'mail', 'status', 'role'],
                        [x.strip() for x in line.split(',')]))
            self.update(data)
        time.sleep(5)
        self.send_confirmation(message.sender)


routes = [
    AdminHandler.mapping(),
]

handlers = webapp2.WSGIApplication(routes, debug=True)
