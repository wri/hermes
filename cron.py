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

import datetime
import webapp2
from google.appengine.api import mail
import model


class CronHandler(webapp2.RequestHandler):

    def send_update(self, subscriber, urlsafe, now):
        """Sends update reminder email to subscriber."""
        day = "{:%b %d, %Y}".format(now)
        reply_to = 'Hermes <update+%s@hermes-hub.appspotmail.com>' % urlsafe
        mail.send_mail(
            sender=reply_to,
            to=subscriber.mail,
            reply_to=reply_to,
            subject='[Hermes] Loop us in for %s' % day,
            body="""Just reply with a few brief bullets starting with *""")

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
            self.send_update(subscriber, urlsafe, now)

    def send_digest(self, subscriber, digest, date):
        """Sends update reminder email to subscriber."""
        day = "{:%b %d, %Y}".format(date)
        reply_to = 'Hermes <noreply@hermes-hub.appspotmail.com>'
        mail.send_mail(
            sender=reply_to,
            to=subscriber.mail,
            reply_to=reply_to,
            subject='[Hermes] Team updates for %s' % day,
            body="""Team updates for %s\n\n%s""" % (day, digest))

    def digest(self):
        update = model.Update.latest()
        s_updates = [x for x in
                     model.SubscriberUpdate.by_date(update.date) if x.message]
        entries = ['%s:\n%s\n\n.....................\n\n' %
                   (x.name, x.message)
                   for x in s_updates]
        digest = ''.join(entries)
        for subscriber in model.Subscriber.subscribed():
            if self.request.get('test'):
                if subscriber.mail == 'asteele@wri.org':
                    self.send_digest(subscriber, digest, update.date)
            else:
                self.send_digest(subscriber, digest, update.date)

routes = [
    webapp2.Route('/cron/update', handler=CronHandler,
                  handler_method='update'),
    webapp2.Route('/cron/digest', handler=CronHandler,
                  handler_method='digest'),
]

handlers = webapp2.WSGIApplication(routes, debug=True)
