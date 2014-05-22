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

import update


class TestHermes(unittest.TestCase):

    def setUp(self):
        pass

    def test_process_update_email(self):
        bodies = {
            "*line1\n*line2\n*line3": "* line1\n* line2\n* line3",
            "*line1\r\n*line2\r\n*line3": "* line1\n* line2\n* line3",
            "*line1\r\n": "* line1",
            "*line1*line2 *line3": "* line1\n* line2\n* line3"}
        for body, expected in bodies.iteritems():
            message = update.UpdateHandler.process(body)
            self.assertEqual(message, expected)

if __name__ == '__main__':
    reload(update)
    unittest.main(exit=False)
