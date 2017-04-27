# -*- coding: utf-8 -*-
# test_service.py
# Copyright (C) 2016 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import unittest

from leap.bitmask.mail.imap.mailbox import make_collection_listener


class _mbox(object):
    pass


class TestListener(unittest.TestCase):

    def setUp(self):
        pass

    def test_mailbox_listener(self):
        mbox1 = _mbox()
        mbox1.mbox_name = 'inbox'

        mbox2 = _mbox()
        mbox2.mbox_name = 'inbox'

        mbox3 = _mbox()
        mbox3.mbox_name = 'trash'

        _set1 = set([mbox1] + [make_collection_listener(mbox2)] +
                    [make_collection_listener(mbox3)])
        assert len(_set1) == 3

        _set2 = set([make_collection_listener(mbox1)] +
                    [make_collection_listener(mbox2)] +
                    [make_collection_listener(mbox3)])
        assert len(_set2) == 2
