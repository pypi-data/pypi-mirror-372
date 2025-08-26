# -*- coding: utf-8 -*-

from collective.timestamp.behaviors.timestamp import ITimestampableDocument
from collective.timestamp.interfaces import ITimeStamper
from plone.indexer import indexer


@indexer(ITimestampableDocument)
def is_timestamped(obj):
    handler = ITimeStamper(obj)
    return handler.is_timestamped()
