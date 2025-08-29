Registered Data Collectors (Control Hub)
========================================
|
Once a Data Collector instance is started, it can be registered with an organization on a Control Hub instance. Those
instances are referred to as Registered Data Collectors, and are only accessible from within the organization they
were registered with.

Updating Data Collector Resource Thresholds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Control Hub can limit the amount of resources consumed on a Data Collector instance, regardless of the workload, to
ensure that no Data Collector is ever overloaded. To check the resource thresholds configured for a given
:py:class:`streamsets.sdk.sch_models.DataCollector` instance, you can reference the ``max_cpu_load``,
``max_memory_used``, and ``max_pipelines_running`` attributes:

.. code-block:: python

    data_collector = sch.data_collectors[0]
    data_collector.max_cpu_load
    data_collector.max_memory_used
    data_collector.max_pipelines_running

**Output:**

.. code-block:: python

    # data_collector.max_cpu_load
    100.0

    # data_collector.max_memory_used
    1000000000000

    # data_collector.max_pipelines_running
    1000000000000

To set new values for the resource thresholds, you can use the :py:meth:`streamsets.sdk.ControlHub.update_data_collector_resource_thresholds`
method to pass in the :py:class:`streamsets.sdk.sch_models.DataCollector` instance and values you wish to set:

.. code-block:: python

    sch.update_data_collector_resource_thresholds(data_collector,
                                                  max_cpu_load=51.5,
                                                  max_memory_used=550,
                                                  max_pipelines_running=25)
    data_collector.max_cpu_load

**Output:**

.. code-block:: python

    51.5
