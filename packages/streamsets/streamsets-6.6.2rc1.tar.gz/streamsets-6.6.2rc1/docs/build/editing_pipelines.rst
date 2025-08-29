Editing Pipelines
=================
|
Editing Pipelines in the Platform SDK follows the structure and conventions that you're already familiar with in the UI,
while offering an extensible, programmatic interaction with pipeline objects.

For more details on Pipeline interaction and usage in the UI, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Pipelines/Pipelines_title.html>`_
for pipelines.

.. hint::
    All of the examples below have focused on stages for SDC pipelines, however :py:class:`streamsets.sdk.sch_models.SchStStage` instances could be swapped into these examples for Transformer pipelines without issue.

Retrieving An Existing Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In the Pipeline UI, you can see your existing Pipelines, and click into them as necessary, seen below

.. image:: ../_static/images/build/existing_pipelines.png
|
|
The :py:attr:`streamsets.sdk.ControlHub.pipelines` attribute can be used to retrieve all your Pipelines.
This attribute returns a :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Pipeline` objects:

.. code-block:: python

    sch.pipelines

Alternatively, you can retrieve specific pipelines by specifying ``pipeline_id``, ``name``, ``version``, or ``commit_id`` to filter the pipeline results
when calling the :py:meth:`streamsets.sdk.utils.SeekableList.get` or :py:meth:`streamsets.sdk.utils.SeekableList.get_all` methods:

.. code-block:: python

    pipeline = sch.pipelines.get(name='Test Pipeline')
    all_version_1_pipelines = sch.pipelines.get_all(version='1')

    pipeline
    all_version_1_pipelines

**Output:**

.. code-block:: python

    # pipeline
    <Pipeline (pipeline_id=5b67c7dc-729b-43cc-bee7-072d3feb184b:admin, commit_id=491cf010-da8c-4e63-9918-3f5ef3b182f6:admin, name=Test Pipeline, version=1)>

    # all_version_1_pipelines
    [<Pipeline (pipeline_id=88d58863-7e8b-4831-a929-8c56db629483:admin,
                commit_id=600a7709-6a13-4e9b-b4cf-6780f057680a:admin,
                name=Test Pipeline,
                version=1)>,
     <Pipeline (pipeline_id=5b67c7dc-729b-43cc-bee7-072d3feb184b:admin,
                commit_id=491cf010-da8c-4e63-9918-3f5ef3b182f6:admin,
                name=Test Pipeline 2,
                version=1)>]

.. _adding-stages-to-existing-pipeline:

Adding Stages To An Existing Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the pipeline is created, you can add stages to it using the Pipeline Canvas UI, seen below:

.. image:: ../_static/images/build/stages_unconnected.png
|
|
To add stages to an existing pipeline using the SDK, utilize the :py:meth:`streamsets.sdk.sch_models.Pipeline.add_stage`
method - see the API reference for this method for details on the arguments this method accepts.

As shown in the image above, the simplest type of pipeline directs one origin into one destination.
To recreate the example above via the SDK, you would use the ``Dev Raw Data Source`` origin and ``Trash`` destination, respectively:

.. code-block:: python

    dev_raw_data_source = pipeline.add_stage('Dev Raw Data Source')
    trash = pipeline.add_stage('Trash')

.. note::
  ``Dev Raw Data Source`` origin cannot be used in Transformer for Snowflake pipelines.
  Instead, use ``Snowflake Table`` or ``Snowflake Query``

Once the desired stages have been added to the pipeline, you can connect them to the other stages in the pipeline as detailed in the :ref:`Connecting the Stages<connecting_stages>` section.

Retrieving Existing Stages In a Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working with an existing :py:class:`streamsets.sdk.sch_models.Pipeline` instance that you want to update, the first step will be retrieving the stage instances to be modified.
To retrieve the :py:class:`streamsets.sdk.sch_models.SchSdcStage` instances you want to update, utilize the ``stages`` attribute for a pipeline.
This will return a :py:class:`streamsets.sdk.utils.SeekableList` of stages that can filtered on specific attributes like ``label``, ``instance_name``, ``stage_type``, ``stage_name`` or any of the other various attributes.

Keeping with the example from the screenshot in the above section, you could execute any of the following commands to retrieve the stages in the pipeline:

.. code-block:: python

    # Retrieve the Dev Raw Data Source origin in various ways
    dev_raw_data_source = pipeline.stages.get(label='Dev Raw Data Source 1')
    dev_raw_data_source = pipeline.stages.get(instance_name='DevRawDataSource_1')
    dev_raw_data_source = pipeline.stages.get(stage_type='SOURCE')
    dev_raw_data_source = pipeline.stages.get(stage_name='com_streamsets_pipeline_stage_devtest_rawdata_RawDataDSource')

    # Retrieve the Trash destination in various ways
    trash = pipeline.stages.get(label='Trash 1')
    trash = pipeline.stages.get(instance_name='Trash_1')
    trash = pipeline.stages.get(stage_type='TARGET')
    trash = pipeline.stages.get(stage_name='com_streamsets_pipeline_stage_destination_devnull_NullDTarget')


If you need to retrieve all stages from a pipeline that match a certain criteria, use the :py:meth:`streamsets.sdk.utils.SeekableList.get_all` method:

.. code-block:: python

    # Retrieve ALL destination stages, for example
    destination_stages_list = pipeline.stages.get_all(stage_type='TARGET')

Copy the Lanes of a Stage
~~~~~~~~~~~~~~~~~~~~~~~~~

When working with an existing :py:class:`streamsets.sdk.sch_models.SchSdcStage` instance, you can copy it's input and output lanes to another :py:class:`streamsets.sdk.sch_models.SchSdcStage` instance within the same Pipeline.

To copy input lanes in the SDK, simply pass in the :py:class:`streamsets.sdk.sch_models.SchSdcStage` object that you wish to copy into the :py:meth:`streamsets.sdk.sch_models.SchSdcStage.copy_inputs` method.
In order to override all the input lanes of the current stage with the input lanes of the passed in :py:class:`streamsets.sdk.sch_models.SchSdcStage` object,  simply set ``override`` to ``True`` within the :py:meth:`streamsets.sdk.sch_models.SchSdcStage.copy_inputs` method:

.. code-block:: python

    # copy input lanes of dev_identity into data_parser
    data_parser.copy_inputs(dev_identity)
    # override data_parser's input lanes with that of dev_identity
    data_parser.copy_inputs(dev_identity, override=True)

To copy output lanes in the SDK, simply pass in the :py:class:`streamsets.sdk.sch_models.SchSdcStage` object that you wish to copy into the :py:meth:`streamsets.sdk.sch_models.SchSdcStage.copy_outputs` method.

.. code-block:: python

    # copy output lanes of dev_identity into data_parser
    data_parser.copy_outputs(dev_identity)

.. note::
  The :py:meth:`streamsets.sdk.sch_models.SchSdcStage.copy_inputs` and :py:meth:`streamsets.sdk.sch_models.SchSdcStage.copy_outputs` methods only work for stages within the same :py:class:`streamsets.sdk.sch_models.Pipeline` or :py:class:`streamsets.sdk.sch_models.PipelineBuilder` instance.

Disconnecting Stages In a Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To disconnect stages on the Pipeline Canvas in the UI, click on the stage's connection and click the Trash icon on the pop-up that appears, shown below:

.. image:: ../_static/images/build/delete_connection.png
|
|
To disconnect output lanes in the SDK, simply pass in the :py:class:`streamsets.sdk.sch_models.SchSdcStage` object to disconnect into the :py:meth:`streamsets.sdk.sch_models.SchSdcStage.disconnect_output_lanes` method.
In order to disconnect all stages receiving output from a specific stage, simply set ``all_stages`` to ``True`` within the :py:meth:`streamsets.sdk.sch_models.SchSdcStage.disconnect_output_lanes` method:

.. code-block:: python

    # disconnect dev_raw_data_source from trash
    dev_raw_data_source.disconnect_output_lanes(stages=[trash])
    # disconnect all stages receiving output from the dev_raw_data_source stage
    dev_raw_data_source.disconnect_output_lanes(all_stages=True)

To disconnect input lanes in the SDK, simply pass in the :py:class:`streamsets.sdk.sch_models.SchSdcStage` object to disconnect into the :py:meth:`streamsets.sdk.sch_models.SchSdcStage.disconnect_input_lanes` method.
In order to disconnect a specific stage from all other stages it receives input from, simply set ``all_stages`` to ``True`` within the :py:meth:`streamsets.sdk.sch_models.SchSdcStage.disconnect_input_lanes` method:

.. code-block:: python

    # disconnect trash from dev_raw_data_source
    trash.disconnect_input_lanes(stages=[dev_raw_data_source])
    # disconnect trash from all other stages it receives input from
    trash.disconnect_input_lanes(all_stages=True)

.. note::
  It is not necessary to call both :py:meth:`streamsets.sdk.sch_models.SchSdcStage.disconnect_output_lanes` and :py:meth:`streamsets.sdk.sch_models.SchSdcStage.disconnect_input_lanes` to break the connection between two stages.
  Calling just one of these methods will disconnect the stages from one another.

Removing Stages From An Existing Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once a stage has been added, you can remove that stage using the Pipeline Canvas UI, seen below:

.. image:: ../_static/images/build/remove_stage.png
|
|
To remove stages from an existing pipeline using the SDK, utilize the :py:meth:`streamsets.sdk.sch_models.Pipeline.remove_stages`
method - see the API reference for this method for details on the arguments this method accepts.

To use the SDK to delete the stage as shown in the example above, you would delete the ``Trash`` destination as seen below:

.. code-block:: python

    pipeline.remove_stage(trash)

.. note::
  Removing a stage from an existing :py:class:`streamsets.sdk.sch_models.Pipeline` instance also removes all output & input lane references that any connected stages had to this stage.

Editing Pipeline/Stage Configuration Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Once a stage has been added, you can edit it's configuration values in the Pipeline Canvas like so:

.. image:: ../_static/images/build/edit_configuration.png
|
|
To edit configuration values in the SDK, you can access the ``configuration`` property in the :py:class:`streamsets.sdk.sch_models.Pipeline` or :py:class:`streamsets.sdk.sch_models.SchSdcStage` object

For example, if you wanted to check the ``configuration`` value of the ``dev_raw_data_source`` stage, you could do the following:

.. code-block:: python

    dev_raw_data_source.configuration.stop_after_first_batch
**Output:**

.. code-block:: python

    False

Setting the configuration value is as simple as directly setting the value in-memory:

.. code-block:: python

    dev_raw_data_source.configuration.stop_after_first_batch = True

.. note::
  The same workflow can be followed to access/edit configuration values of :py:class:`streamsets.sdk.sch_models.Pipeline` objects

Some configuration values have a predefined set of options to choose from.
You can get a list of these using the :py:meth:`streamsets.sdk.sch_models.PipelineBuilder.get_stage_configuration_options` method, as shown below:

.. code-block:: python

    pipeline_builder.get_stage_configuration_options(
        config_name="JSON Content",         # UI name of the configuration field
        stage_name="Dev Raw Data Source",   # Name of the stage
        config_name_type="label",           # Type of the config_name parameter (Default: label)
        stage_name_type="label",            # Type of the stage_name parameter (Default: label)
    )
**Output:**

.. code-block:: python:

    [ChooseOption(UI_VALUE='JSON array of objects', SDK_VALUE='ARRAY_OBJECTS'), ChooseOption(UI_VALUE='Multiple JSON objects', SDK_VALUE='MULTIPLE_OBJECTS')]

The list will match the values shown in the `JSON Content` UI dropdown.

.. image:: ../_static/images/build/value_chooser__JSON_content.png

.. tip::
    Refer to the :ref:`Instantiating a Pipeline Builder<instantiate_builder>` section for creating a Pipeline Builder instance.

|
|
Once you have edited your :py:class:`streamsets.sdk.sch_models.Pipeline` or :py:class:`streamsets.sdk.sch_models.SchSdcStage`, the changes must be published to Control Hub.
This can be done by taking the updated :py:class:`streamsets.sdk.sch_models.Pipeline` instance and passing it into the :py:meth:`streamsets.sdk.sch.publish_pipeline` method as seen below:

.. code-block:: python

    sch.publish_pipeline(pipeline, commit_message='My Edited Pipeline')

Bringing It All Together
~~~~~~~~~~~~~~~~~~~~~~~~

The complete scripts from this section can be found below. Commands that only served to verify some output from the
example have been removed.

.. code-block:: python

    from streamsets.sdk import ControlHub

    sch = ControlHub(credential_id='<credential_id>', token='<token>')

    #all_pipelines = sch.pipelines
    #all_version_1_pipelines = sch.pipelines.get_all(version='1')
    pipeline = sch.pipelines.get(name='Test Pipeline')

    dev_raw_data_source = pipeline.add_stage('Dev Raw Data Source')
    trash = pipeline.add_stage('Trash')

    # Retrieve the Dev Raw Data Source origin in various ways
    dev_raw_data_source = pipeline.stages.get(label='Dev Raw Data Source 1')
    #dev_raw_data_source = pipeline.stages.get(instance_name='DevRawDataSource_1')
    #dev_raw_data_source = pipeline.stages.get(stage_type='SOURCE')
    #dev_raw_data_source = pipeline.stages.get(stage_name='com_streamsets_pipeline_stage_devtest_rawdata_RawDataDSource')

    # Retrieve the Trash destination in various ways
    trash = pipeline.stages.get(label='Trash 1')
    #trash = pipeline.stages.get(instance_name='Trash_1')
    #trash = pipeline.stages.get(stage_type='TARGET')
    #trash = pipeline.stages.get(stage_name='com_streamsets_pipeline_stage_destination_devnull_NullDTarget')

    # Retrieve ALL destination stages
    destination_stages_list = pipeline.stages.get_all(stage_type='TARGET')

    # Remove trash from the Pipeline
    #pipeline.remove_stages(trash)

    dev_raw_data_source.configuration.stop_after_first_batch = True

    sch.publish_pipeline(pipeline, commit_message='My Edited Pipeline')

