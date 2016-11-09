# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from dateutil.tz import gettz

import unittest

from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser

from collective.notices.testing import \
    COLLECTIVE_NOTICES_INTEGRATION_TESTING

from plone.app.testing import login


class TestNotices(unittest.TestCase):

    layer = COLLECTIVE_NOTICES_INTEGRATION_TESTING

    def setUp(self):
        from collective.notices.interfaces import INoticesStorage, INoticesQuery
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.storage = getUtility(INoticesStorage, context=self.portal)
        self.query = getUtility(INoticesQuery, context=self.portal)
        login(self.portal, 'manager')
        self.add_test_data(dict(text=u'blabla'))

    def add_test_data(self, *items):
        from collective.notices.interfaces import INoticeFactory
        for item in items:
            self.storage[INameChooser(self.storage).chooseName()] = \
                INoticeFactory(self.storage)(**item)

    def test_simple(self):
        self.assertEquals(len(self.storage), 1)

    def test_query(self):
        self.assertEquals(len(self.storage), 1)
        now = datetime.now()
        self.add_test_data(
            dict(text=u'aaa', expiration_date=now - timedelta(10)),
            dict(text=u'bbb', effective_date=now + timedelta(10)),
            dict(text=u'ccc', expiration_date=now - timedelta(10), effective_date=now + timedelta(10)),
        )
        L = list(self.query.filter())
        self.assertEquals([x.text for x in L], ['blabla'])
        L = list(self.query.filter(excluded=[int(L[0].__name__)]))
        self.assertEquals(L, [])

    def test_tzinfo(self):
        """creating a notice automatically adds timezone info
        """

        from collective.notices.notice import Notice
        now = datetime.now()

        # create notice w/o dates should work too
        Notice(text='foo')

        # dates shall get tzinfo automatically
        self.assertIsNone(now.tzinfo)
        notice = Notice(text='no-timezone',
                        effective_date=now,
                        expiration_date=now + timedelta(10))
        self.assertIsNotNone(notice.expiration_date,
                             'tzinfo has not been added')
        self.assertIsNotNone(notice.effective_date,
                             'tzinfo has not been added')
