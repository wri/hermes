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
import datetime
import webapp2
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import model


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

    def receive(self, message):
        name, mail = email.Utils.parseaddr(message.sender)
        if not mail in _ADMINS:
            return
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        for line in body.splitlines():
            data = dict(zip(['name', 'mail', 'status', 'role'],
                        [x.strip() for x in line.split(',')]))
            self.update(data)


class UpdateHandler(InboundMailHandler):
    """Handler for incoming update emails from subscribers."""

    def receive(self, message):
        if message.to.find('<') > -1:
            urlsafe = message.to.split('<')[1].split('+')[1].split('@')[0]
        else:
            urlsafe = message.to.split('+')[1].split('@')[0]
        subscriber_update = ndb.Key(urlsafe=urlsafe).get()
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        subscriber_update.message = body
        subscriber_update.put()


class CronHandler(webapp2.RequestHandler):

    def send_update(self, subscriber, urlsafe):
        """Sends update reminder email to subscriber."""
        reply_to = 'update+%s@hermes-hub.appspotmail.com' % urlsafe
        mail.send_mail(
            sender=reply_to,
            to=subscriber.mail,
            reply_to=reply_to,
            subject='[GFW Team Update] Loop us in...',
            body="""Just shoot us a few high level bullet points.""")

    def update(self):
        """Sends update reminder emails to all subscribers."""
        now = datetime.datetime.now()
        update = model.Update(id=now.isoformat(), date=now)
        update.put()
        for subscriber in model.Subscriber.subscribed():
            subscriber_update = model.SubscriberUpdate(
                name=subscriber.name, email=subscriber.mail, date=now)
            subscriber_update.put()
            urlsafe = subscriber_update.key.urlsafe()
            self.send_update(subscriber, urlsafe)

    def digest(self):
        pass

routes = [
    webapp2.Route('/cron/update', handler=CronHandler,
                  handler_method='update'),
    webapp2.Route('/cron/digest', handler=CronHandler,
                  handler_method='digest'),
    AdminHandler.mapping(),
    UpdateHandler.mapping(),
]

handlers = webapp2.WSGIApplication(routes, debug=True)
