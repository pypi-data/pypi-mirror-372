Configuring stages
==================
|
In practice, it's rare to have stages in your pipeline that haven't had some configurations
changed from their default values. When using the SDK, the names to use when referring
to these configuration properties can generally be inferred from the StreamSets Data Collector UI (e.g.
``Data Format`` becomes ``data_format``), but they can also be directly inspected in a Python
interpreter using the :py:func:`dir` built-in function on an instance of the
:py:class:`streamsets.sdk.sdc_models.Stage` class:

.. code-block:: python

    dir(dev_raw_data_source)

or by using Python's built-in :py:func:`help` function:

.. code-block:: python

    help(dev_raw_data_source)

.. image:: ../../_static/dev_raw_data_source_help.png

|

With the attribute name in hand, you can read the value of the configuration:

.. code-block:: python

    dev_raw_data_source.max_line_length

**Output:**

.. code-block:: python

    1024

As for setting the value of the configuration, this can be done in one of two ways
depending on your use case:

Single configurations
~~~~~~~~~~~~~~~~~~~~~

If you only have one or two configurations to update, you can set them using attributes of the
:py:class:`streamsets.sdk.sdc_models.Stage` instance. Continuing in the vein of our example above:

.. code-block:: python

    dev_raw_data_source.data_format = 'TEXT'
    dev_raw_data_source.raw_data = 'hi\nhello\nhow are you?'

Multiple configurations
~~~~~~~~~~~~~~~~~~~~~~~

For readability, it's sometimes better to set all attributes simultaneously with
one call to the :py:meth:`streamsets.sdk.sdc_models.Stage.set_attributes` method:

.. code-block:: python

    dev_raw_data_source.set_attributes(data_format='TEXT', raw_data='hi\nhello\nhow are you?')

