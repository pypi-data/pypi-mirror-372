

=========
Changelog
=========




.. towncrier release notes start

6.17.0 (2025-08-27)
===================

Deprecations and Removals
-------------------------

- Dropped support for migrating old password hashes that were replaced in devpi-server 4.2.0.

- Removed support for basic authorization in primary URL. The connection is already secured by a bearer token header.

- Removed the experimental ``--replica-cert`` option. The replica is already using a token via a shared secret, so this is redundant.

- Removed ``--replica-max-retries`` option. It wasn't implemented for async_httpget and didn't work correctly when streaming data.

Features
--------

- Use httpx for all data fetching for mirrors and fetch projects list asynchronously to allow update in background even after a timeout.

- Use httpx instead of requests when proxying from replicas to primary.

- Use httpx for all requests from replicas to primary.

- Use httpx when pushing releases to external index.

- Added ``mirror_ignore_serial_header`` mirror index option, which allows switching from PyPI to a mirror without serials header when set to ``True``, otherwise only stale links will be served and no updates be stored.

- The HTTP cache information for mirrored projects is persisted and re-used on server restarts.

- Added ``--file-replication-skip-indexes`` option to skip file replication for ``all``, by index type (i.e. ``mirror``) or index name (i.e. ``root/pypi``).

Bug Fixes
---------

- Correctly handle lists for ``Provides-Extra`` and ``License-File`` metadata in database.

- Fix traceback by returning 401 error code when using wrong password with a user that was created using an authentication plugin like devpi-ldap which passes authentication through in that case.

- Fix #1053: allow users to update their passwords when ``--restrict-modify`` is used.

- Fix #1097: return 404 when trying to POST to +simple.

Other Changes
-------------

- Changed User-Agent when fetching data for mirrors from just "server" to "devpi-server".


6.16.0 (2025-06-25)
===================

Deprecations and Removals
-------------------------

- Dropped support for Python 3.7 and 3.8.

Features
--------

- Update stored package metadata fields to version 2.4 for license expressions (PEP 639).

Bug Fixes
---------

- Preserve hash when importing mirror data to prevent unnecessary updates later on.

- Keep original metadata_version in database.


6.15.0 (2025-05-18)
===================

Features
--------

- Add ``--connection-limit`` option to devpi-server passed on to waitress.


6.14.0 (2024-10-16)
===================

Features
--------

- Allow pushing of versions which only have documentation and no releases.

- Allow pushing of release files only with no documentation. Requires devpi-client 7.2.0.

- Allow pushing of documentation only with no release files. Requires devpi-client 7.2.0.

Bug Fixes
---------

- No longer automatically "register" a project when pushing releases to PyPI. The reply changed from HTTP status 410 to 400 breaking the upload. With devpi-client 7.2.0 there is a ``--register-project`` option if it is still required for some other package registry.


6.13.0 (2024-09-19)
===================

Deprecations and Removals
-------------------------

- Remove/Deprecate "master" related terminology in favor of "primary".
  Usage related changes are the switch to ``--primary-url`` instead of ``--master-url`` and ``--role=primary`` instead of ``--role=master``.
  Using the old terms will now output warnings.
  The ``+status`` API has additional fields and the ``role`` field content will change with 7.0.0.

Features
--------

- Enable logging command line options for all commands.

- Added support uv pip as an installer.

Bug Fixes
---------

- Don't report on lagging event processing while replicating.

- Report primary serial correctly with streaming replication.

- Don't store file data in memory when fetching a release while pushing from a mirror.

- Only warn about replica not being in sync instead of fatal status while still replicating.

