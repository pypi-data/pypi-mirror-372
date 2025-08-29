.. readme-start

StreamSets SDK for Python
=========================

The StreamSets SDK for Python enables users to interact with StreamSets products
programmatically using Python 3.4+. As an example, with a running instance of StreamSets Data
Collector, you can create and import a functional pipeline in less than 10 lines of code:

.. code-block:: python

    from streamsets.sdk import DataCollector
    server_url = 'http://localhost:18630'
    data_collector = DataCollector(server_url)

    builder = data_collector.get_pipeline_builder()
    dev_data_generator = builder.add_stage('Dev Data Generator')
    trash = builder.add_stage('Trash')

    dev_data_generator >> trash  # connect the Dev Data Generator origin to the Trash destination.

    pipeline = builder.build('My first pipeline')
    data_collector.add_pipeline(pipeline)

The resulting pipeline can be examined by opening the StreamSets Data Collector user interface
and selecting the ``My first pipeline`` pipeline:

.. readme-end

.. image:: docs/_static/dev_data_generator_to_trash.png
    :width: 75%
