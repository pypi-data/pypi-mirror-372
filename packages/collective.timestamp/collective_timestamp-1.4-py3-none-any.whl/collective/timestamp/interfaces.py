# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from collective.timestamp import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveTimestampLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ITimeStamper(Interface):
    """"""


class ITimestampingSettings(Interface):

    timestamping_service_url = schema.URI(
        title=_("URL of the timestamping service you want to use"),
        default="http://freetsa.org/tsr",
        required=True,
    )

    hashing_algorithm = schema.Choice(
        title=_("Hashing algorithm to use for timestamping"),
        description=_(
            "Choose the hashing algorithm that will be used for generating timestamps."
        ),
        values=["sha1", "sha256", "sha384", "sha512"],
        default="sha256",
        required=True,
    )

    max_retries = schema.Int(
        title=_("Maximum number of retries for timestamping"),
        description=_(
            "The maximum number of attempts to retry timestamping in case of failure."
        ),
        default=0,
        required=True,
    )

    initial_backoff_seconds = schema.Float(
        title=_("Initial backoff time in seconds"),
        description=_(
            "The initial time to wait before retrying a failed timestamping attempt."
        ),
        default=0.5,
        required=True,
    )

    use_failover = schema.Bool(
        title=_("Use failover timestamping"),
        description=_(
            "If enabled, additional timestamping services will be used if the main service is unavailable."
        ),
        default=False,
        required=False,
    )

    failover_timestamping_service_urls = schema.List(
        title=_("List of failover timestamping service URLs"),
        description=_(
            "These services will be used if the main service is unavailable."
        ),
        value_type=schema.URI(),
        default=[],
        required=False,
    )

    timestamping_documentation_url = schema.URI(
        title=_("URL of the documentation explaining how to verify timestamps"),
        default="https://www.freetsa.org/index_en.php",
        required=True,
    )
