Connecting to Data Collector
============================

Credentials
-----------

If no user credentials are passed to :py:class:`streamsets.sdk.DataCollector` when it's being instantiated,
:py:attr:`streamsets.sdk.sdc.DEFAULT_SDC_USERNAME` and :py:attr:`streamsets.sdk.sdc.DEFAULT_SDC_PASSWORD` will be
used for the ``username`` and ``password`` arguments, respectively:

.. code-block:: python

    sdc = DataCollector('http://localhost:18630', username='<username>', password='<password>')

If your Data Collector instance is registered with StreamSets Control Hub, your Control Hub
:ref:`credentials <control hub credentials>` need to be used to instantiate an instance of
:py:class:`streamsets.sdk.ControlHub` before it's passed as an argument to :py:class:`streamsets.sdk.DataCollector`
instead:

.. code-block:: python

    sdc = DataCollector('http://localhost:18630', control_hub=sch)

Connecting to Data Collector using a signed certificate
-------------------------------------------------------

To connect to an HTTPS-enabled Data Collector using a certificate, utilize the attribute
:py:attr:`streamsets.sdk.DataCollector.VERIFY_SSL_CERTIFICATES`:

.. code-block:: python

    from streamsets.sdk import DataCollector
    DataCollector.VERIFY_SSL_CERTIFICATES = '/path/to/certfile'
    sdc = DataCollector('https://localhost:18630')

To skip verifying SSL certificate:

.. code-block:: python

    from streamsets.sdk import DataCollector
    DataCollector.VERIFY_SSL_CERTIFICATES = False
    sdc = DataCollector('https://localhost:18630')

Getting the ID
--------------
You can get the ID for the StreamSets Data Collector instance and verify the correct instance has been connected to:

.. code-block:: python

    sdc.id

**Output:**

.. code-block:: python

    a67344ff-72e9-11ea-af9c-ff111e534c98

.. _sdc_pipeline:

