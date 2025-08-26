# -*- coding: utf-8 -*-

from collective.timestamp import _
from collective.timestamp.interfaces import ITimestampingSettings
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout


class TimestampingControlPanelForm(RegistryEditForm):
    label = _("Timestamping settings")
    schema = ITimestampingSettings


TimestampingControlPanelView = layout.wrap_form(
    TimestampingControlPanelForm, ControlPanelFormWrapper
)
