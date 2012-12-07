
from datetime import datetime

from BTrees.IFBTree import weightedIntersection, union, difference, IFSet

from zope.interface import implements
from zope.component import adapts, getUtility, getMultiAdapter
from zope.catalog.catalog import Catalog, ResultSet

from zc.catalog.catalogindex import SetIndex, ValueIndex, DateTimeValueIndex
from zope.index.interfaces import IIndexSort

from five import grok
import hurry.query

from .interfaces import ICatalogFactory, INoticesStorage, INotice, INoticesQuery


class ResultSet:
    """Lazily accessed set of objects."""

    def __init__(self, uids, storage):
        self.uids = uids
        self.storage = storage

    def __len__(self):
        return len(self.uids)

    def __iter__(self):
        for uid in self.uids:
            obj = self.storage[unicode(uid)]
            yield obj


class NoticesQuery(grok.GlobalUtility):

    grok.provides(INoticesQuery)
    
    @staticmethod
    def AND(a, b):
        if not b:
            if not a:
                return IFSet()
            return a
        if not a:
            return IFSet()
        _, res = weightedIntersection(a, b)
        return res
    
    @staticmethod
    def OR(a, b):
        if not b:
            if not a:
                return IFSet()
            return a
        if not a:
            return IFSet()
        return union(a, b)

    def _apply(self, index, term):
        return index.apply(term) or IFSet()
    
    def all(self):
        storage = getUtility(INoticesStorage)
        return ResultSet(storage.keys(), storage)
    
    def filter(self, users_and_groups=None, **kwargs):
        
        now = datetime.now()
        
        storage = getUtility(INoticesStorage)
        catalog = storage.catalog
        
        # filter out inactive items
        
        active_index = catalog['active']
        
        result = self._apply(
            catalog['active'],
            dict(any_of=(True,))
        )
        
        all = IFSet(active_index.ids())
        
        # filter out items with effective_date > now
        
        effective_date_index = catalog['effective_date']
        
        result = self.AND(
            result,
            self.OR(
                self._apply(effective_date_index, dict(between=(now,))),
                difference(all, IFSet(effective_date_index.ids())) # None value
            )
        )

        # filter out items with expiration_date < now

        expiration_date_index = catalog['expiration_date']
        
        result = self.AND(
            result,
            self.OR(
                self._apply(expiration_date_index, dict(between=(None, now))),
                difference(all, IFSet(expiration_date_index.ids())) # None value
            )
        )
        
        return ResultSet(result, storage)


class CatalogFactory(grok.Adapter):
    
    grok.context(INoticesStorage)
    grok.provides(ICatalogFactory)

    indexes = dict(
        active=ValueIndex,
        effective_date=DateTimeValueIndex,
        expiration_date=DateTimeValueIndex,
        users_and_groups=SetIndex,
    )

    def __call__(self):
        catalog = Catalog()
        for attr, idx_factory in self.indexes.iteritems():
            catalog[attr] = idx_factory(attr, INotice)
        return catalog
