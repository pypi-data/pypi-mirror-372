# -*- coding: utf-8 -*-

from collective.timestamp import _
from collective.timestamp.interfaces import ITimeStamper
from plone import api


def modified_content(obj, event):
    handler = ITimeStamper(obj)
    if not handler.is_timestamped():
        # object is not timestamped, nothing to do here
        return
    if not handler.file_has_changed(obj, event):
        # primary file didn't change, nothing to do
        return
    # primary file field has changed, we need to remove timestamp
    obj.timestamp = None
    obj.reindexObject(idxs=["is_timestamped"])
    request = getattr(obj, "REQUEST", None)
    if request is not None:
        message = _("Timestamp information has been removed since the data has changed")
        api.portal.show_message(message, request)


def warn_on_edition(obj, event):
    handler = ITimeStamper(obj)
    if not handler.is_timestamped():
        # object is not timestamped, no need to warn the user
        return
    request = getattr(obj, "REQUEST", None)
    if request is not None:
        message = _(
            "You are editing a timestamped content. Your modifications can invalidate the timestamp."
        )
        api.portal.show_message(message, request, type="warning")
