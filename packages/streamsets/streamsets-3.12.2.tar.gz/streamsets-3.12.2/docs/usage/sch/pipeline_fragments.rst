Pipeline Fragments
==================
|
A pipeline fragment is a stage or set of connected stages that are frequently used in pipelines. Fragments exist to
quickly and easily add the same logic to multiple pipelines, while centralizing the configuration and design within a
single object.

Fragments are directly accessible via the SDK, including creating new fragments, managing existing fragments, and
adding fragments to a pipeline.

Creating a fragment
~~~~~~~~~~~~~~~~~~~

Creating a new fragment instance is almost identical to creating a pipeline - fragments themselves are
actually still :py:class:`streamsets.sdk.sch_models.Pipeline` objects. The only difference is that we specify
``fragment=True`` when initializing the :py:class:`streamsets.sdk.sch_models.PipelineBuilder` object thus signifying
this object is a pipeline fragment rather than a full pipeline. Use the :py:meth:`streamsets.sdk.ControlHub.get_pipeline_builder`
method to instantiate the builder object:

.. code-block:: python

    # Initialize fragment builder
    pipeline_builder = sch.get_pipeline_builder(fragment=True)

    # Add stages to the pipeline builder
    dev_data_generator = pipeline_builder.add_stage('Dev Data Generator')
    expression_evaluator = pipeline_builder.add_stage('Expression Evaluator')
    field_renamer = pipeline_builder.add_stage('Field Renamer')

    # Connect the stages
    dev_data_generator >> [expression_evaluator, field_renamer]

    # Build and publish the pipeline fragment
    fragment = pipeline_builder.build('Test Fragment')
    sch.publish_pipeline(fragment)

.. image:: ../../_static/sample_fragment.png

Retrieving a Pipeline Fragment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieving pipeline fragments is very similar to the steps for retrieving pipelines.

Because the :py:attr:`streamsets.sdk.ControlHub.pipelines` attribute returns a :py:class:`streamsets.sdk.utils.SeekableList`
of :py:class:`streamsets.sdk.sch_models.Pipeline` objects, you can filter the list by providing ``fragment=True``
when calling :py:meth:`streamsets.sdk.utils.SeekableList.get` or :py:meth:`streamsets.sdk.utils.SeekableList.get_all`:

.. code-block:: python

    sch.pipelines.get_all(fragment=True)

**Output:**

.. code-block:: python

    [<Pipeline (pipeline_id=88d58863-7e8b-4831-a929-8c56db629483:admin,
                commit_id=600a7709-6a13-4e9b-b4cf-6780f057680a:admin,
                name=Dev as fragment,
                version=1)>,
     <Pipeline (pipeline_id=5b67c7dc-729b-43cc-bee7-072d3feb184b:admin,
                commit_id=491cf010-da8c-4e63-9918-3f5ef3b182f6:admin,
                name=Test Fragment,
                version=1)>]

Alternatively, you can retrieve a specific pipeline fragment the same way you would any other pipeline: by specifying
``pipeline_id``, ``name``, or ``commit_id`` to filter the pipeline results:

.. code-block:: python

    pipeline_fragment = sch.pipelines.get(name='Test fragment', fragment=True)
    pipeline_fragment
    pipeline_fragment.fragment

**Output:**

.. code-block:: python

    # pipeline_fragment
    <Pipeline (pipeline_id=5b67c7dc-729b-43cc-bee7-072d3feb184b:admin, commit_id=491cf010-da8c-4e63-9918-3f5ef3b182f6:admin, name=Test Fragment, version=1)>

    # pipeline_fragment.fragment
    True

Using a fragment in a pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding a fragment to a pipeline is almost identical to adding a stage to a pipeline builder. Once you've
retrieved the fragment object you wish to add to the pipeline, simply add it to the :py:class:`streamsets.sdk.sch_models.PipelineBuilder`
instance via the :py:meth:`streamsets.sdk.sch_models.PipelineBuilder.add_fragment` method (inherited from
:py:meth:`streamsets.sdk.sdc_models.PipelineBuilder.add_fragment`), it can be treated like any other stage within the
pipeline builder:

.. code-block:: python

    pipeline_builder = sch.get_pipeline_builder()

    # Retrieve the fragment object to add to the pipeline
    fragment = sch.pipelines.get(fragment=True, name='Test Fragment')

    # Add the fragment to the pipeline builder, which returns a Stage object
    fragment_stage = pipeline_builder.add_fragment(fragment)

    # Add other stages to the pipeline using add_stage
    trash1 = pipeline_builder.add_stage('Trash')
    trash2 = pipeline_builder.add_stage('Trash')

    # Connect the fragment to the other stages
    fragment_stage >> trash1
    fragment_stage >> trash2

    # Build and publish the pipeline
    pipeline = pipeline_builder.build('Test Pipeline')
    sch.publish_pipeline(pipeline)

.. image:: ../../_static/sample_pipeline_using_fragment.png

Retrieving Pipelines that use a specific Pipeline Fragment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve all the pipelines that use a specific fragment, you can pass ``using_fragment=<fragment>`` when
calling :py:meth:`streamsets.sdk.utils.SeekableList.get` or :py:meth:`streamsets.sdk.utils.SeekableList.get_all` -
similar to what is done when retrieving pipeline fragments. The ``using_fragment`` parameter expects a
:py:class:`streamsets.sdk.sch_models.Pipeline` object on which to filter the results:

.. code-block:: python

    # Retrieve the fragment object to be used for the lookup
    fragment = sch.pipelines.get(fragment=True, name='Test Fragment')

    # Retrieve all pipelines from Control Hub that use the fragment retrieved above
    sch.pipelines.get_all(using_fragment=fragment)

**Output:**

.. code-block:: python

    [<Pipeline (pipeline_id=0e1a42c9-7ce3-4295-84dd-ff53a7b313c3:admin,
                commit_id=f3479d83-6e52-4f85-824c-e8ef4185d8f6:admin,
                name=Test Pipeline,
                version=1)>]

Updating an existing pipeline with new fragment version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a fragment is updated and a new version is committed, the pipelines that use that fragment need to be updated to
use the latest version.
To update pipelines that use a specific fragment with the new version of that fragment, you can use the
:py:meth:`streamsets.sdk.ControlHub.update_pipelines_with_different_fragment_version` method. This method expects a
list of :py:class:`streamsets.sdk.sch_models.Pipeline` objects to be updated, as well as two
:py:class:`streamsets.sdk.sch_models.PipelineCommit` objects that represent the fragment version to upgrade from and the
fragment version to upgrade to:

.. code-block:: python

    # Get the fragment object that was updated
    fragment = sch.pipelines.get(fragment=True, name='Test Fragment')

    # Get the old fragment version to upgrade from, and the new fragment version to upgrade to
    from_fragment_version = fragment.commits.get(version='1')
    to_fragment_version = fragment.commits.get(version='2')

    # Get a SeekableList of all pipelines that are currently using the fragment in question, and then pass the list
    # to the update_pipelines_with_different_fragment_version() method
    pipelines = sch.pipelines.get_all(using_fragment=fragment)
    sch.update_pipelines_with_different_fragment_version(pipelines=pipelines,
                                                         from_fragment_version=from_fragment_version,
                                                         to_fragment_version=to_fragment_version)


