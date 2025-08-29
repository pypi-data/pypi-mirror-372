Connecting Stages
=================
|
As described in earlier sections and as shown in the :ref:`first example <first-example>`, connecting stages together
to create the flow of your pipeline is essential to its use.

Output Lanes
------------
To connect the output lane of one stage to the input lane of another, simply use the ``>>`` operator between two
:py:class:`streamsets.sdk.sdc_models.Stage` instances:

.. code-block:: python

    dev_raw_data_source >> trash

For stages with multiple output paths, the ``>>`` operator can be used multiple times:

.. code-block:: python

    file_tail = builder.add_stage('File Tail')
    file_tail >> trash_1
    file_tail >> trash_2

.. image:: ../../_static/file_tail_to_two_trashes.png

|

It is also possible to connect a stage with a single output path to the inputs of multiple stages.

To accomplish this, the ``>>`` operator expects that the :py:class:`streamsets.sdk.sdc_models.Stage` instances, to which
you'll be connecting the same output, are put into a list:

.. code-block:: python

    trash_1 = builder.add_stage('Trash')
    trash_2 = builder.add_stage('Trash')
    dev_raw_data_source >> [trash_1, trash_2]

Using the above steps creates a pipeline like the one in the image below:

.. image:: ../../_static/dev_data_generator_to_two_trashes.png

Event Lanes
-----------

To connect the event lane of one stage to another, use the ``>=`` operator:

.. code-block:: python

    dev_data_generator >> trash_1
    dev_data_generator >= trash_2

|
.. image:: ../../_static/dev_data_generator_with_events.png
