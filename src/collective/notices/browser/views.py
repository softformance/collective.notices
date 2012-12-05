
import json

from zope.interface import implements, alsoProvides
from zope.component import getMultiAdapter
from zope import schema
from zope.container.interfaces import INameChooser

from z3c.form import form, button, field
from plone.z3cform import layout
from plone.z3cform.interfaces import IWrappedForm 
from plone.directives import form

from OFS.SimpleItem import SimpleItem

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from five import grok

from ..interfaces import INotice, INoticesStorage, INoticeFactory


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

    def render(self):
        alsoProvides(self, IWrappedForm)
        if self._finishedAdd:
            return json.dumps(dict(status='success'))
        return super(AddNotice, self).render()


class EditNotice(form.SchemaEditForm):

    grok.context(INotice)
    grok.require('cmf.ManagePortal')
    grok.name('edit')
    
    schema = INotice
    
    _finishedSave = False
    
    errors = {}

    label = u"Edit Notice"
    
    @button.buttonAndHandler(u'Save', name='save')
    def handleApply(self, action):
        self._finishedSave = True
        data, errors = self.extractData()
        if errors:
            self.errors = errors
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

    @button.buttonAndHandler(u'Cancel', name='cancel')
    def handleCancel(self, action):
        pass

    def render(self):
        alsoProvides(self, IWrappedForm)
        if not self._finishedSave or self.errors:
            return super(EditNotice, self).render()
        return getMultiAdapter((self.context, self.request), name='view')()


class ViewNotice(grok.View):
    
    grok.context(INotice)
    grok.require('zope2.View')
    grok.name('view')

