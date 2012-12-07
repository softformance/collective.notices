
from BTrees.OOBTree import OOBTree

from OFS.SimpleItem import SimpleItem

from zope.interface import implements
from zope.container.ordered import OrderedContainer
from zope.cachedescriptors.property import Lazy

from .notice import Notice

from .interfaces import INoticesStorage, ICatalogFactory


class NoticesStorage(SimpleItem, OrderedContainer):
    """The notices storage.
    """
    
    __name__ = u''
    
    implements(INoticesStorage)
    
    def __init__(self):
        super(NoticesStorage, self).__init__()
        self._data = OOBTree()
    
    @property
    def id(self):
        return '++notices++'
    
    @Lazy
    def catalog(self):
        return ICatalogFactory(self)()

