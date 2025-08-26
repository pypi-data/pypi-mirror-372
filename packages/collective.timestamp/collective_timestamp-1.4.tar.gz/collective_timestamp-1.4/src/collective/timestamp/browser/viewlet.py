# -*- coding: utf-8 -*-

from collective.timestamp.interfaces import ITimeStamper
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TimestampViewlet(common.ViewletBase):
    index = ViewPageTemplateFile("templates/viewlet.pt")

    def available(self):
        handler = ITimeStamper(self.context)
        return handler.is_timestamped()
