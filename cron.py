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

    def send_update(self, subscriber, urlsafe):
        """Sends update reminder email to subscriber."""
        reply_to = 'Hermes <update+%s@hermes-hub.appspotmail.com>' % urlsafe
        mail.send_mail(
            sender=reply_to,
            to=subscriber.mail,
            reply_to=reply_to,
            subject='[Hermes] Loop us in...',
            body="""Just reply to this email and shoot us a few high level bullet points. Basically one-liners starting with "*". For example:\n* Secured 1 billion for GFW over next 3 years\n* Briefed POTUS on national GFW impact over lunch\n* Added 3 centimeter resolution UMD data to website""")

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

    def send_digest(self, subscriber, digest, date):
        """Sends update reminder email to subscriber."""
        week = "{:%b %d, %Y}".format(date)
        reply_to = 'Hermes <noreply@hermes-hub.appspotmail.com>'
        mail.send_mail(
            sender=reply_to,
            to=subscriber.mail,
            reply_to=reply_to,
            subject='[Hermes] Looping you in for the week of %s' % week,
            body="""Week of %s\n\n%s""" % (week, digest))

    def digest(self):
        update = model.Update.latest()
        s_updates = [x for x in
                     model.SubscriberUpdate.by_date(update.date)]
        entries = ['%s:\n%s\n\n.....................\n\n' % (x.name, x.message)
                   for x in s_updates]
        digest = ''.join(entries)
        for subscriber in model.Subscriber.subscribed():
            self.send_digest(subscriber, digest, update.date)

routes = [
    webapp2.Route('/cron/update', handler=CronHandler,
                  handler_method='update'),
    webapp2.Route('/cron/digest', handler=CronHandler,
                  handler_method='digest'),
]

handlers = webapp2.WSGIApplication(routes, debug=True)
