Creating a pipeline
===================
|
Once the authentication step has been handled and you've successfully instantiated a :py:class:`streamsets.sdk.DataCollector`
object, you're now ready to build a pipeline.

Instantiating a Pipeline Builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first step of creating a pipeline is to instantiate a :py:class:`streamsets.sdk.sdc_models.PipelineBuilder` instance.
This class handles the majority of the pipeline configuration on your behalf by building the initial JSON representation
of the pipeline, and configuring default values for essential properties (instead of requiring each to be set manually).
The :py:class:`streamsets.sdk.sdc_models.PipelineBuilder` instance can be created as follows:

.. code-block:: python

    pipeline_builder = sdc.get_pipeline_builder()

Adding Stages to the Pipeline Builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that the builder has been instantiated, you can get :py:class:`streamsets.sdk.sdc_models.Stage` instances from this
builder for use in the pipeline you're creating. Adding stages to the pipeline can be done by calling
:py:meth:`streamsets.sdk.sdc_models.PipelineBuilder.add_stage`. See the API reference for this method for details on the
arguments it takes.

As shown in the :ref:`first example <first-example>`, the simplest type of pipeline directs one origin into one
destination. For this example, you can do this with ``Dev Raw Data Source`` origin and ``Trash`` destination,
respectively:

.. code-block:: python

    dev_raw_data_source = pipeline_builder.add_stage('Dev Raw Data Source')
    trash = pipeline_builder.add_stage('Trash')

Connecting the Stages
~~~~~~~~~~~~~~~~~~~~~

With :py:class:`streamsets.sdk.sdc_models.Stage` instances in hand, you can connect them by using the ``>>`` operator.
Once the stages are connected, you can build the :py:class:`streamsets.sdk.sdc_models.Pipeline` instance with the
:py:meth:`streamsets.sdk.sdc_models.PipelineBuilder.build` method:

.. code-block:: python

    dev_raw_data_source >> trash
    pipeline = pipeline_builder.build('My first pipeline')

Add the Pipeline to Data Collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, to add this pipeline to your Data Collector instance, pass it to the
:py:meth:`streamsets.sdk.DataCollector.add_pipeline` method:

.. code-block:: python

    sdc.add_pipeline(pipeline)


