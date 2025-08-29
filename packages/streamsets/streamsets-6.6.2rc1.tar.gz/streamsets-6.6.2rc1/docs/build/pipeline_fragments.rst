Pipeline Fragments
==================
|
A pipeline fragment is a stage or set of connected stages that are frequently used in pipelines. Fragments exist to
quickly and easily add the same logic to multiple pipelines, while centralizing the configuration and design within a
single object.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Pipeline_Fragments/PipelineFragments_title.html>`_
for fragments.

Fragments are directly accessible via the SDK, including creating new fragments, managing existing fragments, and
adding fragments to a pipeline.

Creating a Fragment
~~~~~~~~~~~~~~~~~~~

From the Platform UI, creating a fragment is very similar to creating a pipeline. Clicking 'Create New
Pipeline Fragment' in the Fragments UI presents a canvas with which to add or modify stages as seen below:

.. image:: ../_static/images/build/fragment_canvas.png
|
|
In the SDK, creating a new fragment instance is almost identical to creating a pipeline - fragments themselves are
:py:class:`streamsets.sdk.sch_models.Pipeline` objects. The only difference is the need to specify
``fragment=True`` when initializing the :py:class:`streamsets.sdk.sch_models.PipelineBuilder` object thus signifying
this object is a pipeline fragment rather than a full pipeline. Use the :py:meth:`streamsets.sdk.ControlHub.get_pipeline_builder`
method to instantiate the builder object, and pass in the relevant ``engine_type`` and ``engine_id`` alongside the
``fragment`` parameter.

.. note::
  Similar to pipelines, the ``engine_id`` is **required** for the ``'data_collector'`` and ``'transformer'``
  engine types when creating a pipeline fragment but should not be specified for the ``'snowflake'`` engine type.
  Additionally, ``fragment=True`` **must** be supplied when creating a pipeline fragment.

The following code creates a fragment identical to the one seen in the screenshot above:

.. code-block:: python

    # Initialize fragment builder
    sdc = sch.engines.get(engine_url='<data_collector_url>')
    pipeline_builder = sch.get_pipeline_builder(engine_type='data_collector', engine_id=sdc.id, fragment=True)

    # Add stages to the pipeline builder
    dev_data_generator = pipeline_builder.add_stage('Dev Data Generator')
    expression_evaluator = pipeline_builder.add_stage('Expression Evaluator')
    field_renamer = pipeline_builder.add_stage('Field Renamer')

    # Connect the stages
    dev_data_generator >> [expression_evaluator, field_renamer]

    # Build and publish the pipeline fragment
    fragment = pipeline_builder.build('Test Fragment')
    sch.publish_pipeline(fragment)

Retrieving a Pipeline Fragment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieving the available pipeline fragments in the Platform UI can be done by simply selecting the Fragments
option from the navigation menu, as seen below:

.. image:: ../_static/images/build/fragment_ui.png
|
|
In the SDK, retrieving pipeline fragments is very similar to the steps for retrieving pipelines.

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

    pipeline_fragment = sch.pipelines.get(name='Test Fragment', fragment=True)
    pipeline_fragment
    pipeline_fragment.fragment

**Output:**

.. code-block:: python

    # pipeline_fragment
    <Pipeline (pipeline_id=5b67c7dc-729b-43cc-bee7-072d3feb184b:admin, commit_id=491cf010-da8c-4e63-9918-3f5ef3b182f6:admin, name=Test Fragment, version=1)>

    # pipeline_fragment.fragment
    True

Using a Fragment in a Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once a fragment is created and checked in, it can be used within a pipeline. From the Platform UI, Fragments
appear as another stage on the pipeline canvas as seen below:

.. image:: ../_static/images/build/add_frag_to_pipeline.png
|
|
Adding a fragment to a pipeline using the SDK is almost identical to adding a stage to a pipeline builder. Once you've
retrieved the fragment object you wish to add to the pipeline, simply add it to the :py:class:`streamsets.sdk.sch_models.PipelineBuilder`
instance via the :py:meth:`streamsets.sdk.sch_models.PipelineBuilder.add_fragment` method. It can then be treated like
any other stage within the pipeline builder.

The following code adds a fragment to a pipeline with two additional trash stages, creating the pipeline seen in the
screenshot above:

.. code-block:: python

    sdc = sch.engines.get(engine_url='<data_collector_url>')
    pipeline_builder = sch.get_pipeline_builder(engine_type='data_collector', engine_id=sdc.id)

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

Retrieving Pipelines That Use a Specific Pipeline Fragment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To find out which pipelines in your Platform organization are making use of a particular fragment, the Fragments
UI provides an informational pane in the canvas as seen below:

.. image:: ../_static/images/build/pipelines_using_fragment.png
|
|
To retrieve all the pipelines that use a specific fragment in the SDK, you can pass in the ``using_fragment=<fragment>``
parameter when calling :py:meth:`streamsets.sdk.utils.SeekableList.get` or :py:meth:`streamsets.sdk.utils.SeekableList.get_all`
- similar to what is done when retrieving pipeline fragments. The ``using_fragment`` parameter expects a
:py:class:`streamsets.sdk.sch_models.Pipeline` object on which to filter the results:

.. code-block:: python

    # Retrieve the fragment object to be used for the lookup
    fragment = sch.pipelines.get(fragment=True, name='Test Fragment')

    # Retrieve all pipelines from Platform that use the fragment retrieved above
    sch.pipelines.get_all(using_fragment=fragment)

**Output:**

.. code-block:: python

    [<Pipeline (pipeline_id=0e1a42c9-7ce3-4295-84dd-ff53a7b313c3:admin,
                commit_id=f3479d83-6e52-4f85-824c-e8ef4185d8f6:admin,
                name=Test Pipeline,
                version=1)>]

Updating an Existing Pipeline With a New Fragment Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a fragment is updated and a new version is committed, the pipelines that use that fragment need to be updated to
use the latest version.

The Fragments UI provides you with an option to update any and all pipelines with the latest version of the fragment
upon check in, as seen below:

.. image:: ../_static/images/build/update_pipeline_with_frag.png
|
|
In the SDK, you can use the :py:meth:`streamsets.sdk.ControlHub.update_pipelines_with_different_fragment_version` method
to update pipelines that use a specific fragment with the new version of that fragment. This method expects a
list of :py:class:`streamsets.sdk.sch_models.Pipeline` objects to be updated, as well as two
:py:class:`streamsets.sdk.sch_models.PipelineCommit` objects that represent the fragment version to upgrade from and the
fragment version to upgrade to:

.. code-block:: python

    # Get the fragment object that was updated
    fragment = sch.pipelines.get(fragment=True, name='Test Fragment')

    # Get the old fragment version to upgrade from, and the new fragment version to upgrade to
    from_fragment_version = fragment.commits.get(version='1')
    to_fragment_version = fragment.commits.get(version='2')

    # Get a SeekableList of all pipelines that are currently using the old fragment version in question.
    # Then pass the list to the update_pipelines_with_different_fragment_version() method
    pipelines = sch.pipelines.get_all(using_fragment=from_fragment_version)
    sch.update_pipelines_with_different_fragment_version(pipelines=pipelines,
                                                         from_fragment_version=from_fragment_version,
                                                         to_fragment_version=to_fragment_version)

Bringing It All Together
~~~~~~~~~~~~~~~~~~~~~~~~

The complete script from this section can be found below. Commands that only served to verify some output from the
example have been removed, as have any overlapping/redundant commands.

.. code-block:: python

    from streamsets.sdk import ControlHub

    sch = ControlHub(credential_id='<credential_id>', token='<token>')
    sdc = sch.engines.get(engine_url='<data_collector_url>')

    # ---- CREATING THE PIPELINE FRAGMENT ----
    # Initialize fragment builder
    pipeline_builder = sch.get_pipeline_builder(engine_type='data_collector', engine_id=sdc.id, fragment=True)
    # Add stages to the pipeline builder
    dev_data_generator = pipeline_builder.add_stage('Dev Data Generator')
    expression_evaluator = pipeline_builder.add_stage('Expression Evaluator')
    field_renamer = pipeline_builder.add_stage('Field Renamer')
    # Connect the stages
    dev_data_generator >> [expression_evaluator, field_renamer]
    # Build and publish the pipeline fragment
    fragment = pipeline_builder.build('Test Fragment')
    sch.publish_pipeline(fragment)

    # ---- ADDING THE FRAGMENT TO A PIPELINE ----
    pipeline_builder = sch.get_pipeline_builder(engine_type='data_collector', engine_id=sdc.id)
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

    # ---- UPDATING THE VERSION OF A FRAGMENT USED IN A PIPELINE ----
    # Get the fragment object that was updated
    fragment = sch.pipelines.get(fragment=True, name='Test Fragment')
    # Get the old fragment version to upgrade from, and the new fragment version to upgrade to
    from_fragment_version = fragment.commits.get(version='1')
    to_fragment_version = fragment.commits.get(version='2')
    # Get a SeekableList of all pipelines that are currently using the old fragment version in question.
    # Then pass the list to the update_pipelines_with_different_fragment_version() method
    pipelines = sch.pipelines.get_all(using_fragment=from_fragment_version)
    sch.update_pipelines_with_different_fragment_version(pipelines=pipelines,
                                                         from_fragment_version=from_fragment_version,
                                                         to_fragment_version=to_fragment_version)
