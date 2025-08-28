Owly plugin for `Tutor <https://docs.tutor.edly.io>`__
######################################################

Bring the power of AI to Open edX with Owly!

To know more about Owly and book a demo, visit `GetOwly.ai <https://getowly.ai>`__.

Note
****

You do not need this plugin to run Owly.
This Tutor plugin enhances Owly when used with Open edX by:

- Adding extra API endpoints in Open edX to enable advanced features (analytics, course management, roles, etc.).
- Injecting the Owly chat widget into all LMS and MFE pages when ``OWLY_ENABLE_CHAT`` is enabled.

Installation
************

.. code-block:: bash

    pip install git+https://github.com/aulasneo/tutor-contrib-owly

Usage
*****

.. code-block:: bash

    tutor plugins enable owly
    tutor images build openedx
    tutor images build mfe
    tutor local start

Configuration
*************

The following settings are available:

- ``OWLY_ENABLE_CHAT``: Enable the chat feature. Default: ``False``

When enabling the chat feature, this plugin injects the Owly chat into all LMS and MFE pages.
You will need to build the MFE image and restart the environment.

Note: Do not enable the chat if you are using a custom ``frontend-platform``; otherwise it will be overwritten.

How it works
************

Owly itself can run without this plugin.
This plugin integrates Owly with Open edX by:

- Exposing additional backend endpoints used by Owly for advanced capabilities.
- Embedding the Owly chat widget across the LMS/MFE (when ``OWLY_ENABLE_CHAT`` is enabled).

For a complete list of API endpoints, visit `Owly API Reference <https://github.com/aulasneo/openedx-owly-apis>`__.