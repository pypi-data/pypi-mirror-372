from collective.timestamp import logger
from datetime import datetime
from pyasn1.codec.der import decoder
from pyasn1.codec.der import encoder
from rfc3161ng import get_timestamp
from rfc3161ng import RemoteTimestamper
from rfc3161ng import TimeStampResp
from rfc3161ng import TimeStampToken

import pytz
import time


def localize_utc_date(date: datetime):
    tzinfo = pytz.timezone("UTC")
    return tzinfo.localize(date)


def get_timestamp_date(timestamp_token: TimeStampToken, localize=True):
    """
    Extract the timestamp date from a time stamp token.
    :param timestamp_token: The time stamp token to extract the date from.
    :param localize: Whether to localize the date to UTC (default is True).
    :return: The timestamp date, localized if specified.
    """
    timestamp_date = get_timestamp(timestamp_token)
    if localize:
        return localize_utc_date(timestamp_date)
    return timestamp_date


def get_timestamp_date_from_tsr_file(tsr_data: bytes, localize: bool = True):
    """Extracts the timestamp date from a tsr file"""
    tsr, _ = decoder.decode(tsr_data, asn1Spec=TimeStampResp())
    timestamp_token = tsr.time_stamp_token
    return get_timestamp_date(timestamp_token, localize=localize)


def timestamp(
    file_content: bytes,
    service_url: str,
    hashing_algorithm: str = "sha256",
    use_failover: bool = False,
    failover_timestamping_service_urls: list = None,
    max_retries: int = 0,
    initial_backoff_seconds: float = 0.5,
    localize_date: bool = True,
):
    """
    Generate a timestamp for the given file_content using a remote timestamping service.
    It attempts to obtain a timestamp from the (primary) service_url, and if it fails,
    it will switch to one of the failover_timestamping_service_urls if configured.
    It can also use exponential backoff for retries.
    :param file_content: The content of the file to be timestamped.
    :param service_url: The primary timestamping service URL.
    :param hashing_algorithm: The hashing algorithm to use (default is "sha256").
    :param use_failover: Whether to use failover timestamping services if the primary service fails.
    :param failover_timestamping_service_urls: A list of failover timestamping service URLs.
    :param max_retries: The maximum number of retries for timestamping attempts.
    :param initial_backoff_seconds: The initial backoff time in seconds for retrying failed attempts.
    :raises ConnectionError: If all attempts to obtain a timestamp fail.
    :return: A tuple containing the encoded timestamp response and the localized timestamp date.
    """
    success = False
    tsr = None
    # Make a copy to avoid modifying the original list
    failover_urls = (
        failover_timestamping_service_urls.copy()
        if failover_timestamping_service_urls
        else []
    )
    while not success:
        retry_count = 0
        backoff_seconds = initial_backoff_seconds

        # Try main service URL with exponential backoff
        while retry_count <= max_retries:
            try:
                timestamper = RemoteTimestamper(
                    service_url,
                    certificate=b"",
                    hashname=hashing_algorithm,
                )
                tsr = timestamper(
                    data=file_content,
                    include_tsa_certificate=True,
                    return_tsr=True,
                )
                success = True
                break
            except Exception as e:
                retry_count += 1
                logger.error(f"Timestamping attempt {retry_count} failed: {e}")
                if retry_count <= max_retries:
                    logger.info(f"Retrying in {backoff_seconds} seconds...")
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                else:
                    logger.error(
                        f"Reached max retries ({max_retries}) for URL: {service_url}"
                    )

        if success or not use_failover:
            # If we succeeded or not using failover, we can exit the loop
            break

        if use_failover:
            if not failover_urls:
                logger.error("No failover URLs available, cannot proceed.")
                break
            service_url = failover_urls.pop(0)
            logger.info(f"Switching to failover URL: {service_url}")
    if not success:
        raise ConnectionError("Failed to obtain a timestamp.")

    timestamp_token = tsr.time_stamp_token
    timestamp_date = get_timestamp_date(timestamp_token, localize=localize_date)
    return encoder.encode(tsr), timestamp_date
