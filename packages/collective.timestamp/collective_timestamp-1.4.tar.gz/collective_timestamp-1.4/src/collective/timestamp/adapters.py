# -*- coding: utf-8 -*-

from collective.timestamp import logger
from collective.timestamp.interfaces import ITimeStamper
from collective.timestamp.interfaces import ITimestampingSettings
from collective.timestamp.utils import timestamp
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.interfaces import INamedField
from plone.registry.interfaces import IRegistry
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.component import getUtility
from zope.interface import implementer
from zope.lifecycleevent.interfaces import IAttributes


@implementer(ITimeStamper)
class TimeStamper(object):
    """Handle timestamping operations on an object"""

    def __init__(self, context):
        self.context = context

    def get_file_field(self):
        try:
            primary = IPrimaryFieldInfo(self.context, None)
            if (
                INamedField.providedBy(primary.field)
                and hasattr(primary.value, "getSize")
                and primary.value.getSize() > 0
            ):
                return primary
        except TypeError:
            pass

    def get_data(self):
        field = self.get_file_field()
        if field is None:
            logger.warning(
                f"Could not find the file field for {self.context.absolute_url()}"
            )
            return
        return field.value.data

    def file_has_changed(self, obj, event):
        field = self.get_file_field()
        fieldname = field.fieldname
        for d in event.descriptions:
            if not IAttributes.providedBy(d):
                continue
            if fieldname in d.attributes:
                return True
        return False

    def is_timestamped(self):
        return self.context.timestamp is not None

    def is_timestampable(self):
        if not self.context.enable_timestamping:
            return False
        elif self.is_timestamped():
            return False
        return self.get_data() is not None

    def _effective_related_indexes(self):
        return ["effective", "effectiveRange", "is_timestamped"]

    def generate_timestamp(self, file_content: bytes):
        """Produce the .tsr blob and the datetime when it was created, using the registry settings."""
        settings = getUtility(IRegistry).forInterface(ITimestampingSettings)
        return timestamp(
            file_content,
            service_url=settings.timestamping_service_url,
            hashing_algorithm=settings.hashing_algorithm,
            use_failover=settings.use_failover,
            failover_timestamping_service_urls=settings.failover_timestamping_service_urls,
            max_retries=settings.max_retries,
            initial_backoff_seconds=settings.initial_backoff_seconds,
        )

    def timestamp(self):
        """Timestamp this context: attach the .tsr file, set the effective date, and reindex."""
        if not self.is_timestampable():
            raise ValueError("This content is not timestampable")
        data = self.get_data()
        tsr_file, timestamp_date = self.generate_timestamp(data)
        self.context.timestamp = NamedBlobFile(data=tsr_file, filename="timestamp.tsr")
        self.context.setEffectiveDate(timestamp_date)
        self.context.reindexObject(idxs=self._effective_related_indexes())
        # return data and timestamp in case method is overrided
        return data, timestamp_date
