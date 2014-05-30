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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.import unittest

import unittest
import datetime

from google.appengine.ext import testbed

import admin
import update
import model


class TestUpdateHandler(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def test_get_update(self):
        bodies = {
            "*line1\n*line2\n*line3": "* line1\n* line2\n* line3",
            "*line1\r\n*line2\r\n*line3": "* line1\n* line2\n* line3",
            "*line1\r\n": "* line1",
            "*line1*line2 *line3": "* line1\n* line2\n* line3"}
        for body, expected in bodies.iteritems():
            message = update.UpdateHandler.get_update(body)
            self.assertEqual(message, expected)

    def test_get_urlsafe(self):
        f = update.UpdateHandler.get_urlsafe
        tests = {
            'Hermes <update+ag5kZXZ@hermes-hub.appspotmail.com>': 'ag5kZXZ',
            '<update+ag5kZXZ@hermes-hub.appspotmail.com>': 'ag5kZXZ',
            'update+ag5kZXZ@hermes-hub.appspotmail.com': 'ag5kZXZ',
        }
        urlsafe = 'ag5kZXZ'
        for address, urlsafe in tests.iteritems():
            self.assertEqual(f(address), urlsafe)

    def test_process_update(self):
        f = update.UpdateHandler.process_update

        # Create SubscriberUpdate
        date = datetime.datetime.now()
        x = model.SubscriberUpdate.get_or_insert(
            'aaron', 'a@a.com', 'gfw', date)
        urlsafe = x.key.urlsafe()
        address = 'Hermes <update+%s@hermes-hub.appspotmail.com>' % urlsafe
        body = '* did nothing\n* met nobody'
        f(address, body)

        # Check that the update message made it
        key_name = '%s+%s+%s' % ('gfw', 'a@a.com', date.isoformat())
        x = model.SubscriberUpdate.get_by_id(key_name)
        self.assertIsNotNone(x)
        self.assertEqual(x.message, body)


class TestAdminHandler(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

        self.body = 'aaron,aaron@aaron.com,gfw,subscribe,admin\n'
        self.body += '\nnoah, noah@noah.com , gfw, subscribe'

    def tearDown(self):
        self.testbed.deactivate()

    def test_is_admin(self):
        f = admin.AdminHandler.is_admin
        map(self.assertTrue,
            map(f, ['asteele@wri.org', 'cdavis@wri.org', 'dhammer@wri.org',
                    'rkraft@gwri.org', 'alyssa.westerman@wri.org']))
        self.assertFalse(f('wannabe@admin.com'))

    def test_get_subscriptions(self):
        f = admin.AdminHandler.get_subscriptions
        subs = [x for x in f(self.body)]
        sub = dict(name='aaron', mail='aaron@aaron.com', team='gfw',
                   status='subscribe', role='admin')
        self.assertIn(sub, subs)
        sub = dict(name='noah', mail='noah@noah.com', team='gfw',
                   status='subscribe')
        self.assertIn(sub, subs)
        self.assertTrue(len(subs) == 2)

    def test_update_subscriptions(self):
        f = admin.AdminHandler.update_subscription

        # Create new subscription
        data = dict(name='aaron', mail='AARON@AARON.COM', team='GFW',
                    status='subscribe', role='admin')
        f(data)
        sub = model.Subscriber.get_by_id('aaron@aaron.com+gfw')
        expected = dict(name='aaron', mail='aaron@aaron.com', team='gfw',
                        status='subscribe', role='admin')
        self.assertDictContainsSubset(sub.to_dict(), expected)

        # Update existing subscription
        data = dict(name='aaron', mail='AARON@AARON.COM', team='GFW',
                    status='subscribe')
        f(data)
        sub = model.Subscriber.get_by_id('aaron@aaron.com+gfw')
        expected = dict(name='aaron', mail='aaron@aaron.com', team='gfw',
                        status='subscribe', role=None)
        self.assertDictContainsSubset(sub.to_dict(), expected)

        # Create new subscription for existing user on a different team
        data = dict(name='aaron', mail='AARON@AARON.COM', team='POTICO',
                    status='subscribe', role='admin')
        f(data)
        sub = model.Subscriber.get_by_id('aaron@aaron.com+potico')
        self.assertIsNotNone(model)
        expected = dict(name='aaron', mail='aaron@aaron.com', team='potico',
                        status='subscribe', role='admin')
        self.assertDictContainsSubset(sub.to_dict(), expected)

    def test_get_subscription_report(self):
        f = admin.AdminHandler.get_subscription_report
        subs = [dict(name='aaron', mail='aaron@aaron.com', team='gfw',
                     status='subscribe', role='admin'),
                dict(name='aaron', mail='aaron@aaron.com', team='potico',
                     status='subscribe', role='admin')]
        report = f(subs)
        expected = """aaron <aaron@aaron.com> gfw subscribe admin
aaron <aaron@aaron.com> potico subscribe admin"""
        self.assertEqual(report, expected)

    def test_get_subscription_msg(self):
        f = admin.AdminHandler.get_subscription_msg
        report = 'aaron <aaron@aaron.com> gfw subscribe admin'
        to = 'asteele@wri.org'
        msg = f(to, report)
        msg.send()
        messages = self.mail_stub.get_sent_messages(to='asteele@wri.org')
        self.assertEqual(1, len(messages))
        message = messages[0]
        self.assertEqual('asteele@wri.org', message.to)
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        self.assertEqual(report, body)

    def test_process_message(self):
        f = admin.AdminHandler.process_message
        f('asteele@wri.org', self.body)
        messages = self.mail_stub.get_sent_messages(to='asteele@wri.org')
        self.assertEqual(1, len(messages))
        message = messages[0]
        self.assertEqual('asteele@wri.org', message.to)
        report = """aaron <aaron@aaron.com> gfw subscribe admin
noah <noah@noah.com> gfw subscribe None"""
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        self.assertEqual(report, body)
        sub = model.Subscriber.get_by_id('aaron@aaron.com+gfw')
        self.assertIsNotNone(sub)

if __name__ == '__main__':
    reload(update)
    reload(admin)
    unittest.main(exit=False)
