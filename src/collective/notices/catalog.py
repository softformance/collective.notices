
from datetime import datetime

from BTrees.IFBTree import weightedIntersection, union, difference, IFSet

from zope.interface import implements
from zope.component import adapts, getUtility, getMultiAdapter
from zope.catalog.catalog import Catalog, ResultSet

from zc.catalog.catalogindex import SetIndex, ValueIndex, DateTimeValueIndex
from zope.index.interfaces import IIndexSort

from five import grok

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
    
    def __getslice__(self, *args, **kwargs):
        uids = self.uids.__getslice__(*args, **kwargs)
        return self.__class__(uids, self.storage)
        


class NoticesQuery(grok.GlobalUtility):

    grok.provides(INoticesQuery)
    
    @staticmethod
    def intersection(a, b):
        if a and b:
            _, res = weightedIntersection(a, b)
            return res
        return a or b or IFSet()
    
    @staticmethod
    def union(a, b):
        if a and b:
            return union(a, b)
        return a or b or IFSet()

    def _apply(self, index, term):
        return index.apply(term) or IFSet()
    
    def filter(self, users_and_groups=None, excluded=None):
        
        now = datetime.utcnow()
        
        storage = getUtility(INoticesStorage)
        catalog = storage.catalog
        
        active_index = catalog['active']
        
        all = IFSet(active_index.ids())
        
        # filter out inactive items
        
        result = self._apply(
            catalog['active'],
            dict(any_of=(True,))
        )
        
        # filter users and groups
        
        if users_and_groups:
            
            users_and_groups_index = catalog['users_and_groups']
            
            result = self.intersection(
                result,
                self.union(
                    self._apply(
                        users_and_groups_index,
                        dict(any_of=users_and_groups)
                    ),
                    difference(all, IFSet(users_and_groups_index.ids())) # None value
                )
            )
        
        # filter out items with effective_date > now
        
        effective_date_index = catalog['effective_date']
        
        result = self.intersection(
            result,
            self.union(
                self._apply(effective_date_index, dict(between=(now,))),
                difference(all, IFSet(effective_date_index.ids())) # None value
            )
        )

        # filter out items with expiration_date < now

        expiration_date_index = catalog['expiration_date']
        
        result = self.intersection(
            result,
            self.union(
                self._apply(expiration_date_index, dict(between=(None, now))),
                difference(all, IFSet(expiration_date_index.ids())) # None value
            )
        )
        
        # filter out excluded notices
        
        if excluded:
            
            result = difference(result, IFSet(excluded))
        
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
