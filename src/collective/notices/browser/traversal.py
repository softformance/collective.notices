
from zope.interface import implements
from zope.component import adapts, getUtility, getMultiAdapter
from zope.app.component.hooks import getSite

from zope.traversing.interfaces import ITraversable, TraversalError
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.container.traversal import ContainerTraverser
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from five import grok

from Acquisition import aq_base

from Products.CMFCore.interfaces import ISiteRoot

from ..interfaces import INoticesStorage


class NoticesNamespace(grok.MultiAdapter):
    """Used to traverse to a notice.
    """
    
    grok.adapts(ISiteRoot, IHTTPRequest)
    grok.provides(ITraversable)
    grok.name('notices')

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        storage = getUtility(INoticesStorage)
        if storage.__name__ != u'++notices++':
            storage.__name__ = u'++notices++'
        if name:
            N = storage[name]
            id = u'++notices++%s' % N.__name__
            if N.id != id:
                N.id = id
            return N
        return storage
