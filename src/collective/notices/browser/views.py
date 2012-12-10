
import sys
import json
from types import StringTypes

from zope.interface import implements, alsoProvides
from zope.component import getMultiAdapter
from zope import schema
from zope.container.interfaces import INameChooser
from zope.app.component.hooks import getSite
from zope.cachedescriptors.property import Lazy

from z3c.form import form, button, field
from plone.directives import form

from z3c.batching.batch import Batch
from plone.z3cform.crud.crud import BatchNavigation

from five import grok

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage

from ..interfaces import INotice, INoticesStorage, INoticeFactory, INoticesQuery
from ..catalog import ResultSet


class AddNotice(form.SchemaAddForm):
    
    grok.context(INoticesStorage)
    grok.require('cmf.ManagePortal')
    grok.name('add')
    
    schema = INotice
    
    label = u"Add Notice"
    
    def create(self, data):
        return INoticeFactory(self.context)(**data)

    def add(self, ob):
        self.context[INameChooser(self.context).chooseName()] = ob


class EditNotice(form.SchemaEditForm):

    grok.context(INotice)
    grok.require('cmf.ManagePortal')
    grok.name('edit')
    
    schema = INotice

    label = u"Edit Notice"

    def __init__(self, *args, **kwargs):
        super(EditNotice, self).__init__(*args, **kwargs)
        self.request.set('disable_border', True)
    
    @button.buttonAndHandler(u'Save', name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(u"Changes saved", "info")
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(u'Cancel', name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(u"Edit cancelled", "info")
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return getSite().absolute_url() + '/++notices++'


class DeleteNotice(grok.View):
    
    grok.context(INotice)
    grok.require('cmf.ManagePortal')
    grok.name('delete')

    def render(self):
        del self.context.__parent__[self.context.__name__]
        IStatusMessage(self.request).addStatusMessage(u"Item deleted", "info")
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return getSite().absolute_url() + '/++notices++'


class ManageNotices(grok.View):
    
    grok.context(INoticesStorage)
    grok.require('cmf.ManagePortal')
    grok.name('manage')

    def getPrincipalIds(self):
        
        membership = getToolByName(self.context, 'portal_membership', None)
        if membership is None or membership.isAnonymousUser():
            return ()
        
        member = membership.getAuthenticatedMember()
        if not member:
            return ()
        
        groups = hasattr(member, 'getGroups') and member.getGroups() or []

        # Ensure we get the list of ids - getGroups() suffers some acquision
        # ambiguity - the Plone member-data version returns ids.

        for group in groups:
            if type(group) not in StringTypes:
                return ()
        
        return [member.getId()] + groups

    @Lazy
    def notices(self):
        return ResultSet(self.context.keys(), self.context)

    @Lazy
    def batch(self):
        batch_size = 2
        page = int(self.request.get('page', '0'))
        return Batch(self.notices, start=page*batch_size, size=batch_size)

    def render_batch_navigation(self):
        navigation = BatchNavigation(self.batch, self.request)
        def make_link(page):
            return "%s?page=%s" % (self.request.getURL(), page)
        navigation.make_link = make_link
        return navigation()

