from collective.timestamp import logger
from collective.timestamp.behaviors.timestamp import ITimestampableDocument
from collective.timestamp.interfaces import ITimeStamper
from OFS.SimpleItem import SimpleItem
from plone import api
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.base.utils import pretty_title_or_id
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from rfc3161ng import TimestampingError
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class ITimestampAction(Interface):
    """Interface for the configurable aspects of a timestamp action."""


@implementer(ITimestampAction, IRuleElementData)
class TimestampAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "collective.timestamp.actions.Timestamp"
    summary = _("Timestamp object")


@adapter(Interface, ITimestampAction, Interface)
@implementer(IExecutable)
class TimestampActionExecutor:
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        if not obj:
            return False

        if not ITimestampableDocument.providedBy(obj):
            return False
        handler = ITimeStamper(obj)
        if not handler.is_timestampable():
            return False
        try:
            handler.timestamp()
        except TimestampingError as e:
            self.error(obj, str(e))
            logger.error(f"Timestamp rule failed for {obj.absolute_url()} : {str(e)}")
            return False

        logger.info(f"Timestamp generated for {obj.absolute_url()}")
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = pretty_title_or_id(obj, obj)
            message = _(
                "Timestamp file has been successfully generated and saved for ${name}",
                mapping={"name": title},
            )
            api.portal.show_message(message, request)
        return True

    def error(self, obj, error):
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = pretty_title_or_id(obj, obj)
            message = _(
                "Unable to timestamp ${name}: ${error}",
                mapping={"name": title, "error": error},
            )
            api.portal.show_message(message, request, type="error")


class TimestampAddForm(NullAddForm):
    """A degenerate "add form" for timestamp actions."""

    def create(self):
        return TimestampAction()
