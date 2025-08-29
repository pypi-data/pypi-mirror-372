.. module:: streamsets
.. _sdc_usage:
Data Collector Usage
====================
|
The following sections include explanations and examples of the extensive usage and implementation of the StreamSets SDK
for Python, specifically pertaining to the use of the SDK with StreamSets Data Collector.

Importing the DataCollector Module
----------------------------------

The examples below assume you've installed the ``streamsets`` library,
:ref:`activated the library <activation>`, and are inside a Python 3.6+ interpreter.


Use of the SDK begins by importing the library. For convenience, we tend to directly import the classes we need:

.. code-block:: python

    from streamsets.sdk import DataCollector

.. toctree::
   :maxdepth: 2
   :hidden:

   usage/sdc/connecting_to_sdc
   usage/sdc/creating_a_pipeline
   usage/sdc/configuring_stages
   usage/sdc/connecting_stages
   usage/sdc/error_stages
   usage/sdc/pipeline_snapshots
   usage/sdc/importing_exporting_pipelines