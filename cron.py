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

"""This module provides endpoint logic for cron jobs that send team update
reminder emails and digest emails.
"""

import datetime
import functools
import logging
import webapp2

from google.appengine.api import mail

import model


class CronUpdateHandler(webapp2.RequestHandler):

    @classmethod
    def get_reply_address(cls, urlsafe):
        """Return update email reply address given supplied urlsafe string."""
        return 'Hermes <update+%s@hermes-hub.appspotmail.com>' % urlsafe

    @classmethod
    def get_update_message(cls, team, to, sender, date):
        """Return unsent update EmailMessage."""
        day = "{:%b %d, %Y}".format(date)
        fields = dict(
            sender=sender,
            to=to,
            reply_to=sender,
            subject='[Hermes] Send %s updates - %s' % (team.upper(), day),
            body="Just reply with a few brief bullets starting with *")
        return mail.EmailMessage(**fields)

    @classmethod
    def process_subscriber_update(cls, date, subscriber):
        """Create new SubscriberUpdate and send update email to subscriber."""
        subscriber_update = model.SubscriberUpdate.get_or_insert(
            name=subscriber.name, mail=subscriber.mail, team=subscriber.team,
            date=date)
        sender = cls.get_reply_address(subscriber_update.key.urlsafe())
        message = cls.get_update_message(
            subscriber.team, subscriber.mail, sender, date)
        message.send()
        subscriber_update.sent = True
        subscriber_update.put()

    @classmethod
    def process_update(cls, team, date):
        """Create new Update for supplied team and send team update emails."""
        update = model.Update.get_or_insert(team, date=date)
        f = functools.partial(cls.process_subscriber_update, update.date)
        map(f, model.Subscriber.subscribed(team))

    def update(self, team):
        """Sends update reminder emails to all subscribers."""
        self.process_update(team, datetime.datetime.now())


class CronDigestHandler(webapp2.RequestHandler):

    @classmethod
    def get_digest_message(cls, team, digest, date, to):
        """Sends update reminder email to subscriber."""
        day = "{:%b %d, %Y}".format(date)
        reply_to = 'Hermes <noreply@hermes-hub.appspotmail.com>'
        fields = dict(
            sender=reply_to,
            to=to,
            reply_to=reply_to,
            subject='[Hermes] %s team updates - %s' % (team.upper(), day),
            body=digest)
        return mail.EmailMessage(**fields)

    @classmethod
    def get_subscriber_updates(cls, team, date):
        """Return list of SubscriberUpdate for team and date with messages."""
        return [x for x in
                model.SubscriberUpdate.get_updates(date, team)
                if x.message]

    @classmethod
    def get_update(cls, x):
        """Return formatted update string for supplied SubscriberUpdate x."""
        update = x.to_dict()
        update['message'] = update['message'].encode('utf8')
        return '{name} <{mail}>\n{message}\n\n'.format(**update)

    @classmethod
    def process_digest(cls, team, test=None):
        update = model.Update.latest(team)
        if not update:
            logging.info('No Update to process for digest')
            return
        digest = ''.join(
            map(cls.get_update, cls.get_subscriber_updates(team, update.date)))
        if test:
            return digest
        if not digest:
            logging.info('No subscriber updates to process for digest')
            return
        for subscriber in model.Subscriber.subscribed(team):
            subscriber_digest = model.SubscriberDigest.get_or_insert(
                mail=subscriber.mail, team=team, date=update.date)
            if not subscriber_digest.sent:
                message = cls.get_digest_message(
                    team, digest, update.date, subscriber.mail)
                message.send()
                subscriber_digest.sent = True
                subscriber_digest.put()
        return digest

    def digest(self, team):
        test = self.request.get('test')
        if test:
            digest = self.process_digest(team, test=test)
            self.response.out.write(digest)
        else:
            self.process_digest(team)

routes = [
    webapp2.Route('/cron/update/<team:.*>', handler=CronUpdateHandler,
                  handler_method='update'),
    webapp2.Route('/cron/digest/<team:.*>', handler=CronDigestHandler,
                  handler_method='digest'),
]

handlers = webapp2.WSGIApplication(routes, debug=True)
