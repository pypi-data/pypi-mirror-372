Pipeline Labels
---------------
|
Pipeline labels help to categorize and quickly filter specific pipelines based on a keyword or set of keywords.
The SDK allows modification of pipeline labels, as well as creating new pipelines with labels.

Creating a pipeline with labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to specify labels for a pipeline at creation time, you need to supply the desired labels at the time
:py:meth:`streamsets.sdk.sch_models.PipelineBuilder.build` is called for the pipeline being created:

.. code-block:: python

    # Create a list with some labels to apply to the pipeline, and pass those labels in during build time
    labels = ['test/dev', 'test']
    pipeline = pipeline_builder.build(title='Test pipeline with labels', labels=labels)
    sch.publish_pipeline(pipeline)
    pipeline.labels

**Output:**

.. code-block:: python

    [<PipelineLabel (label=test/dev)>,
     <PipelineLabel (label=test)>]

Fetching all pipeline labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK also allows retrieval of all pipeline labels that exist for your organization on Control Hub:

.. code-block:: python

   sch.pipeline_labels

**Output:**

.. code-block:: python

   [<PipelineLabel (label=test/dev)>, <PipelineLabel (label=test)>]

You can also fetch pipeline labels by their parent ID:

.. code-block:: python

    sch.pipeline_labels.get_all(parent_id='test:admin')

**Output:**

.. code-block:: python

    [<PipelineLabel (label=test/dev)>]

Updating labels of an existing pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A very common operation is to take an existing pipeline, and modify the labels assigned to it. This is a simple
operation using the SDK. To add new labels to an existing pipeline, the :py:meth:`streamsets.sdk.sch_models.Pipeline.add_label`
method can be used before publishing the pipeline to Control Hub:

.. code-block:: python

    pipeline = sch.pipelines.get(commit_id=<commit_id>)
    pipeline.add_label('prod/dev', 'prod')
    sch.publish_pipeline(pipeline)
    pipeline.labels

**Output:**

.. code-block:: python

    [<PipelineLabel (label=test/dev)>,
     <PipelineLabel (label=test)>,
     <PipelineLabel (label=prod/dev)>,
     <PipelineLabel (label=prod)>]

Removing existing labels for a pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Removing existing labels from a pipeline can be done in a similar fashion using :py:meth:`streamsets.sdk.sch_models.Pipeline.remove_label`
against an existing pipeline instance:

.. code-block:: python

    pipeline = sch.pipelines.get(commit_id=<commit_id>)
    pipeline.remove_label('test', 'test/dev')
    sch.publish_pipeline(pipeline)
    pipeline.labels

**Output:**

.. code-block:: python

    [<PipelineLabel (label=prod/dev)>,
     <PipelineLabel (label=prod)>]]

Deleting pipeline labels
~~~~~~~~~~~~~~~~~~~~~~~~

Pipeline labels can also be deleted from your Control Hub organization as a whole. First, get an instance of the
:py:class:`streamsets.sdk.sch_models.PipelineLabel` that you wish to remove. Then, call the :py:meth:`streamsets.sdk.ControlHub.delete_pipeline_labels`
method and pass in the label:

.. code-block:: python

    label = sch.pipeline_labels.get(parent_id='test:admin', label='test/dev')
    sch.delete_pipeline_labels(label)

