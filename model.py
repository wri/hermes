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

"""This module contains the model."""

from google.appengine.ext import ndb


class Subscriber(ndb.Model):
    """Represents a single person subscribed to Hermes. The id is the email."""
    name = ndb.StringProperty()
    mail = ndb.StringProperty()
    status = ndb.StringProperty()  # subscribe | unsubscribe
    role = ndb.StringProperty()  # admin | None

    @classmethod
    def subscribed(cls):
        """Return all Subscriber models with a status equal to 'subscribe'."""
        return cls.query(cls.status=='subscribe').fetch(100)


class SubscriberUpdate(ndb.Model):
    """Represents a subscriber update with an Update parent."""
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    message = ndb.TextProperty()
    date = ndb.DateTimeProperty()

    @classmethod
    def by_date(cls, date):
        return cls.query(cls.date==date).fetch(100)


class Update(ndb.Model):
    """Represents all Message objects for a given date."""
    date = ndb.DateTimeProperty()
    digest_sent = ndb.BooleanProperty(default=False)

    @classmethod
    def latest(cls):
        """Returns the latest Update entity."""
        return cls.query().order(-cls.date).get()
