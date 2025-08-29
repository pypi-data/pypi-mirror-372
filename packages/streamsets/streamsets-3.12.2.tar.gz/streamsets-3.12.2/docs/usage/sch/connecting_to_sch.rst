Connecting to Control Hub
=========================

Using Control Hub credentials
-------------------------------------------
.. _control hub credentials:

Connect to Control Hub by creating an instance of :py:class:`streamsets.sdk.ControlHub`, passing in
the URL of your Control Hub instance, your Control Hub username, and your Control Hub password:

.. code-block:: python

    sch = ControlHub('https://cloud.streamsets.com', username=<your username>, password=<your password>)

Using a signed certificate
----------------------------------------------------

To connect to an HTTPS-enabled Control Hub using a certificate, utilize the attribute
:py:attr:`streamsets.sdk.ControlHub.VERIFY_SSL_CERTIFICATES`:

.. code-block:: python

    from streamsets.sdk import ControlHub
    ControlHub.VERIFY_SSL_CERTIFICATES = '/path/to/certfile'
    sch = ControlHub('https://localhost:18631', 'username@org', 'password')

