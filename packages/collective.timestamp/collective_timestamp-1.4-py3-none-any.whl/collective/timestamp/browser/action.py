# -*- coding: utf-8 -*-

from collective.timestamp import _
from collective.timestamp import logger
from collective.timestamp.behaviors.timestamp import ITimestampableDocument
from collective.timestamp.interfaces import ITimeStamper
from plone import api
from Products.Five.browser import BrowserView
from rfc3161ng import TimestampingError


class TimestampView(BrowserView):

    def available(self):
        """
        Show timestamp action only if content is stampable and not already
        stamped.
        """
        if not ITimestampableDocument.providedBy(self.context):
            return False
        handler = ITimeStamper(self.context)
        return handler.is_timestampable()

    def timestamp(self):
        obj = self.context
        redirect_url = f"{obj.absolute_url()}/view"
        handler = ITimeStamper(obj)
        try:
            handler.timestamp()
        except TimestampingError as e:
            api.portal.show_message(
                _("Timestamp has failed."),
                self.request,
                type="error",
            )
            logger.error(f"Timestamp action failed for {obj.absolute_url()} : {str(e)}")
            self.request.response.redirect(redirect_url)
            return ""
        logger.info(f"Timestamp generated for {obj.absolute_url()}")
        api.portal.show_message(
            _("Timestamp file has been successfully generated and saved"), self.request
        )
        self.request.response.redirect(redirect_url)
