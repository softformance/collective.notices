

from zope.interface import implements
from zope.component import adapts, getUtility, getMultiAdapter
from zope.catalog.catalog import Catalog

from zc.catalog.catalogindex import SetIndex, ValueIndex, DateTimeValueIndex

from five import grok

from .interfaces import ICatalogFactory, INoticesStorage, INotice


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
