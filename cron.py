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
import logging
import webapp2
from google.appengine.api import mail
import model


class CronHandler(webapp2.RequestHandler):

    def send_update(self, team, subscriber, subscriber_update, urlsafe, now):
        """Sends update reminder email to subscriber.

        Updates subscriber_update.sent if mail sent and
        subscriber_update.error if there's a mail error.
        """
        try:
            mail.check_email_valid(subscriber.mail, 'msg')
            day = "{:%b %d, %Y}".format(now)
            reply_to = 'Hermes <update+%s@hermes-hub.appspotmail.com>' % \
                urlsafe
            mail.send_mail(
                sender=reply_to,
                to=subscriber.mail,
                reply_to=reply_to,
                subject='[Hermes] Send %s updates - %s' % (team.upper(), day),
                body="Just reply with a few brief bullets starting with *")
            subscriber_update.sent = True
        except (Exception, mail.InvalidEmailError, mail.Error), e:
            subscriber_update.error = e.message
            logging.exception(e)

    def update(self, team):
        """Sends update reminder emails to all subscribers."""
        now = datetime.datetime.now()
        update = model.Update(id=now.isoformat(), date=now, team=team)
        update.put()
        for subscriber in model.Subscriber.subscribed(team):
            subscriber_update = model.SubscriberUpdate.get_or_insert(
                name=subscriber.name, mail=subscriber.mail, team=team,
                date=now)
            if subscriber_update.sent:
                # Update email already sent, so nothing to do here!
                continue
            urlsafe = subscriber_update.key.urlsafe()
            self.send_update(team, subscriber, subscriber_update, urlsafe, now)
            subscriber_update.put()

    def send_digest(self, team, subscriber, digest, date):
        """Sends update reminder email to subscriber."""
        try:
            mail.check_email_valid(subscriber.mail, 'msg')
            sub_digest = model.SubscriberDigest.get_or_insert(
                mail=subscriber.mail, team=team, date=date)
            if sub_digest.sent:
                # Digest email already sent, so nothing to do here!
                return
            day = "{:%b %d, %Y}".format(date)
            reply_to = 'Hermes <noreply@hermes-hub.appspotmail.com>'
            mail.send_mail(
                sender=reply_to,
                to=subscriber.mail,
                reply_to=reply_to,
                subject='[Hermes] %s team updates - %s' % (team.upper(), day),
                body=digest)
            sub_digest.sent = True
        except (Exception, mail.InvalidEmailError, mail.Error), e:
            sub_digest.error = e.message
            logging.exception(e)
        sub_digest.put()

    def digest(self, team):
        update = model.Update.latest(team)
        s_updates = [x for x in
                     model.SubscriberUpdate.get_updates(update.date, team)
                     if x.message]
        entries = ['%s:\n%s\n\n.....................\n\n' %
                   (x.name, x.message)
                   for x in s_updates]
        digest = ''.join(entries)
        if self.request.get('test'):
            self.response.out.write(digest)
        else:
            for subscriber in model.Subscriber.subscribed(team):
                self.send_digest(team, subscriber, digest, update.date)

routes = [
    webapp2.Route('/cron/update/<team:.*>', handler=CronHandler,
                  handler_method='update'),
    webapp2.Route('/cron/digest/<team:.*>', handler=CronHandler,
                  handler_method='digest'),
]

handlers = webapp2.WSGIApplication(routes, debug=True)
