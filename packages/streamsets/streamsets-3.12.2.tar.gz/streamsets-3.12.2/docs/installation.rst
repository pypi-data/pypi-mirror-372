.. _installation:

Installation
============

Using pip
---------

To install the most recent stable release of the library, use your Python 3 installation's instance of `pip`_:

.. code-block:: console

    $ pip3 install streamsets~=3.0

.. note::
  This will install the latest SDK release from the 3.x branch, intended for use with StreamSets Control Hub. Releases
  of the SDK for Python starting with version 4.0.0 are intended for use with the StreamSets DataOps Platform, and are
  incompatible with previous releases of StreamSets Control Hub. Make sure the correct version has been installed before
  proceeding.

.. _pip: https://pip.pypa.io


.. _activation:

Activation
----------

After installing for the first time, the library requires
an activation key to be used. This key can either be placed in the user configuration
directory under ``~/.streamsets`` in a folder called ``activation`` or can be set as an
environment variable called ``STREAMSETS_SDK_ACTIVATION_KEY``. The environment variable, if available,
will only be used if the activation key file is not present. If not present the first time the library is imported, the
directory ``~/.streamsets/activation`` will be created for you automatically.
If this key is not in place, a :py:exc:`streamsets.sdk.exceptions.ActivationError`
will be raised whenever you attempt to create an instance of
:py:class:`streamsets.sdk.DataCollector`:

.. code-block:: python

    from streamsets.sdk import DataCollector
    data_collector = DataCollector('http://localhost:18630')

**Output:**

.. code-block:: python

    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/local/lib/python3.6/site-packages/streamsets/sdk/sdc.py", line 59, in __init__
        **kwargs)
      File "streamsets/sdk/sdc_api.pyx", line 79, in sdk.sdc_api.ApiClient.__init__
      File "streamsets/sdk/sdc_api.pyx", line 85, in sdk.sdc_api.ApiClient._verify_activation
    streamsets.sdk.exceptions.ActivationError: Failed to activate Python SDK for StreamSets (reason: Could not find activation file at /Users/dima/.streamsets/activation/rsa-signed-activation-info.properties or /usr/local/lib/python3.6/site-packages/streamsets/sdk/activation/rsa-signed-activation-info.properties or environment variable STREAMSETS_SDK_ACTIVATION_KEY).

If you have an ``rsa-signed-activation-info.properties`` file, simply place it into the directory
referenced above or set the content of key (without header and footer) to the above referenced environment
variable and retry your command. For example, if your key looks like

.. code-block:: shell

    -------SDC ACTIVATION KEY-----
    abcdefg
    -------SDC ACTIVATION KEY-----

you'd export only the key itself and not the header and footer:

.. code-block:: shell

    $ export STREAMSETS_SDK_ACTIVATION_KEY='abcdefg'

If you don't yet have this activation key, contact StreamSets Support with
a request for access to the SDK for Python.

Versioning
----------

In general, the major and minor release version of the StreamSets SDK for Python should be greater
than or equal to that of the StreamSets Data Collector and/or StreamSets Control Hub instance that
you'd like to interact with. That is, version ``3.2.0`` of the StreamSets SDK for Python
has been tested against StreamSets Data Collector 3.2.0.0 and StreamSets Control Hub 3.2.0.
Compatibility of the StreamSets SDK for Python against earlier versions of StreamSets
Data Collector and StreamSets Control Hub is provided on a best effort basis.
