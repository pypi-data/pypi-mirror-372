# -*- coding: utf-8 -*-

from collective.timestamp import _
from plone import schema
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from zope.interface import provider


@provider(IFormFieldProvider)
class ITimestampableDocument(model.Schema):
    """ """

    model.fieldset(
        "timestamp",
        label=_("Timestamp"),
        fields=["enable_timestamping", "timestamp"],
    )

    read_permission(timestamp="collective.timestamp.read")
    write_permission(timestamp="collective.timestamp.write")
    timestamp = NamedBlobFile(
        title=_("Time Stamp Response (TSR) file"),
        required=False,
    )

    enable_timestamping = schema.Bool(
        title=_("Enable timestamping"),
        description=_(
            "This allows you to disable timestamping for this specific content."
        ),
        default=True,
        required=False,
    )
