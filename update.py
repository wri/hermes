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

import logging
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

from model import SubscriberUpdate


class UpdateHandler(InboundMailHandler):
    """Handler for incoming update emails from subscribers."""

    @classmethod
    def process(cls, body):
        """Process body into lines starting with * and return as string."""
        lines = []
        tokens = body.splitlines()
        if len(tokens) == 1:
            # Hack: Maybe all bullets on same line:
            tokens = ['* %s' % x for x in body.split('*')]
        for x in tokens:
            if not x[1:].strip():
                continue
            if x.strip().startswith('*'):
                x = '* %s' % x[1:].strip()
                lines.append(x)
        message = '\n'.join(lines)
        return message

    def receive(self, message):
        """Updates SubscriberUpdate model message using urlsafe key from
        reply-to address and message contained in the mail body.
        """
        if message.to.find('<') > -1:
            urlsafe = message.to.split('<')[1].split('+')[1].split('@')[0]
        else:
            urlsafe = message.to.split('+')[1].split('@')[0]
        subscriber_update = ndb.Key(urlsafe=urlsafe).get()
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        subscriber_update.message = self.process(body)
        subscriber_update.put()

routes = [
    UpdateHandler.mapping(),
]

handlers = webapp2.WSGIApplication(routes, debug=True)
