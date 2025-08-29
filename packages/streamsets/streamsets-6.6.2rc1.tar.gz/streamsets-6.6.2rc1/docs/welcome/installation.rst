.. _installation:

Installation
============
|

Using pip
---------
The pip3 package manager must be installed on the machine where the SDK will be installed and used.

To install the |version| release of the library, use your Python 3 installation's instance of `pip`_:

.. code-block:: console

    pip3 install streamsets

.. _pip: https://pip.pypa.io


Note: You do not need any activation key.

Versioning
----------

To use the functionality of StreamSets Platform, the major version of StreamSets Platform SDK for
Python should be greater than or equal to 4.0.0.

An engine runs StreamSets pipelines. StreamSets has three engines, Data Collector, Transformer and Transformer for
Snowflake.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Engines/Overview.html#concept_r1f_4kx_t4b>`_.

If you wish to use Data Collector with StreamSets Platform SDK for Python, start and deploy a
Data Collector of version greater than or equal to 4.0.2 with StreamSets Platform.

If you wish to use Transformer with StreamSets Platform SDK for Python, start and deploy a
Transformer of version greater than or equal to 4.0.0 with StreamSets Platform.

If you wish to use Transformer for Snowflake with StreamSets Platform SDK for Python, you don't need to start
any engines, just select the desired execution mode when using the SDK.
