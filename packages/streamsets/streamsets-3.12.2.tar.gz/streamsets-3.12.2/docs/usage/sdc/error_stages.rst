Error Stages
============
|

To add an error stage to a pipeline, use the :py:meth:`streamsets.sdk.sdc_models.PipelineBuilder.add_error_stage`
method:

.. code-block:: python

    discard = builder.add_error_stage('Discard')

By default, the :py:class:`streamsets.sdk.sdc_models.PipelineBuilder` instance will use 'Discard' if no error stage
is specified.

