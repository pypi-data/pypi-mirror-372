translatable-xblocks
####################

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

Plugin for adding translation behavior to XBlocks. This plugin assumes:

1. Translations IDA is setup (https://github.com/edx/ai-translations).

2. Frontend plugin setup to add translation selector.

When present and enabled, requesting a ``src_lang`` and ``dest_lang`` as query params in a unit render
should request and return translated versions of those XBlocks' content.

**WARNING**: This replaces some native XBlocks from ``edx-platform`` and replaces them with custom versions.
While we only override small portions of functionality, there is a chance this will cause things to "spookily"
break. See `translatable_xblocks/apps.py <translatable_xblocks/apps.py>`_ for where we do this block replacement.

Guides
******

- `Quickstart`_.
- `How to test this repository`_.
- `How to deploy this repository`_.

.. _Quickstart: docs/quickstarts/index.rst
.. _How to test this repository: docs/how-tos/test_this_repo.rst
.. _How to deploy this repository: docs/how-tos/deploy_this_repo.rst

Getting Started with Development
********************************

See `quickstart guide`.

.. _quickstart guide: docs/quickstarts/index.rst


Conventions / Rules / Best Practices
====================================

1. Use conventional commits for making commits.

2. Format files with ``black``. Do this and other fixes automatically with ``make format``.

3. Squash commits when merging a PR.

Please see also the Open edX documentation for `guidance on Python development <https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html>`_ in this repo.

Testing
=======

See `how to test this repository`_.

.. _how to test this repository: docs/how-tos/test_this_repo.rst

Deploying
*********

See `how to deploy this repository`_.

.. _how to deploy this repository: docs/how-tos/deploy_this_repo.rst

Getting Help
************

Documentation
=============

PLACEHOLDER: Start by going through `the documentation`_.  If you need more help see below.

.. _the documentation: https://docs.openedx.org/projects/translatable-xblocks

(TODO: `Set up documentation <https://openedx.atlassian.net/wiki/spaces/DOC/pages/21627535/Publish+Documentation+on+Read+the+Docs>`_)

More Help
=========

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/edx/translatable-xblocks/issues

For more information about these options, see the `Getting Help <https://openedx.org/getting-help>`__ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/translatable-xblocks

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/translatable-xblocks.svg
    :target: https://pypi.python.org/pypi/translatable-xblocks/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/edx/translatable-xblocks/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/edx/translatable-xblocks/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/edx/translatable-xblocks/coverage.svg?branch=main
    :target: https://codecov.io/github/edx/translatable-xblocks?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/translatable-xblocks/badge/?version=latest
    :target: https://docs.openedx.org/projects/translatable-xblocks
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/translatable-xblocks.svg
    :target: https://pypi.python.org/pypi/translatable-xblocks/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/translatable-xblocks.svg
    :target: https://github.com/edx/translatable-xblocks/blob/main/LICENSE.txt
    :alt: License

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
