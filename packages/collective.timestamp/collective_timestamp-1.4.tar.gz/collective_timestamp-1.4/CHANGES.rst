Changelog
=========


1.4 (2025-08-26)
----------------

- Add a new view `TimestampInfo` to have more info about the timestamp that can also be used as an util view.
  [aduchene]


1.3 (2025-06-23)
----------------

- Avoid modifying list passed as argument in `utils.timestamp`.
  [aduchene]


1.2 (2025-06-19)
----------------

- Fixed a bug with `utils.timestamp` stuck in an infinite loop when use_failover was False.
  [aduchene]
- Changed default values of `ITimestampingSettings` and set required fields.
  [aduchene]


1.1 (2025-06-19)
----------------

- Fix a bug with TimeStamper.timestamp not returning the correct value.
  [aduchene]


1.0 (2025-06-19)
----------------

- Refactor the `timestamp` utils function to be able to use failover urls and exp. backoff retries.
  [aduchene]
- Add settings to manage failover urls and exp. backoff retries.
  [aduchene]


1.0a2 (2024-10-11)
------------------

- Added `TimeStamper._effective_related_indexes` to factorize the list of
  catalog indexes related to the `effective` functionality.
  Make `TimeStamper.timestamp` return data and timestamp in case it is overrided
  or called from external code.
  [gbastien]


1.0a1 (2024-09-17)
------------------

- Initial release.
  [laulaz]
