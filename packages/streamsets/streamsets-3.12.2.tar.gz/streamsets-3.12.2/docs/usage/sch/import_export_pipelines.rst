Importing and Exporting Pipelines
=================================

Importing a pipeline into Control Hub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can import a pipeline's JSON file into Control Hub in three ways:

1. Import the JSON file into :py:class:`streamsets.sdk.sch_models.PipelineBuilder` and publish the pipeline:

.. code-block::  python

    with open('./exported_from_sdc.json', 'r') as input_file:
        pipeline_json = json.load(input_file)

    sch_pipeline_builder = sch.get_pipeline_builder()
    sch_pipeline_builder.import_pipeline(pipeline=pipeline_json)
    pipeline = sch_pipeline_builder.build(title='Modified using Pipeline Builder')
    sch.publish_pipeline(pipeline)

2. Import a new version of a pipeline from JSON and update the existing pipeline in Control Hub (the existing pipeline
is inferred from the metadata in the pipeline JSON specified):

.. code-block:: python

    with open('./exported_from_sch.json', 'r') as input_file:
        pipeline_json = json.load(input_file)

    sch_pipeline_builder = sch.get_pipeline_builder()
    sch_pipeline_builder.import_pipeline(pipeline=pipeline_json)
    pipeline = sch_pipeline_builder.build(preserve_id=True)
    sch.publish_pipeline(pipeline)

3. Directly import a pipeline from JSON, creating a new pipeline instance in Control Hub:

.. code-block:: python

    with open('./exported_from_sch.json', 'r') as input_file:
        pipeline_json = json.load(input_file)

    pipeline = sch.import_pipeline(pipeline=pipeline_json,
                                   commit_message='Imported pipeline from JSON',
                                   name='My new pipeline')

Exporting and Importing multiple Pipelines at once
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To import multiple pipelines into Control Hub from a zip archive:

.. code-block:: python

    with open('./sdc_exports_for_sch.zip', 'rb') as input_file:
        pipelines_zip_data = input_file.read()
    pipelines = sch.import_pipelines_from_archive(archive=pipelines_zip_data,
                                                  commit_message='Exported as zip from sdc')

Similarly, you can export pipelines from Control Hub using :py:meth:`streamsets.sdk.ControlHub.export_pipelines` to
export one or more pipelines, and write them to a local archive:

.. code-block:: python

    pipeline_list = sch.pipelines.get_all(label='export')

    # Show the pipelines to be exported
    pipeline_list

    # Export the pipelines from Control Hub
    pipeline_export_data = sch.export_pipelines(pipelines=pipeline_list)

    # Write the exported pipeline data to a local archive
    with open ('./sch_pipeline_exports.zip', 'wb') as output_file:
        output_file.write(pipeline_export_data)

**Output:**

.. code-block:: python

    [<Pipeline (pipeline_id=502dfc46-0473-43c1-b020-ebae2df693d9:testorg, commit_id=3681ee3e-e926-4160-98d3-cc975efe9871:testorg, name=SampleOne, version=2)>,
    <Pipeline (pipeline_id=bece23ff-1f5c-48b7-8386-20352bbd7832:testorg, commit_id=da208ed8-34fb-463d-a1b8-cd5f06883dbf:testorg, name=SampleTwo, version=1)>,
    <Pipeline (pipeline_id=a47d2089-0405-418f-bad0-17cc52d4d85a:testorg, commit_id=499e3b71-b9f2-483a-92e6-401ecdb9ae3a:testorg, name=SampleThree, version=3)>]

Duplicating a Pipeline
~~~~~~~~~~~~~~~~~~~~~~

To duplicate an existing pipeline in Control Hub, use the :py:meth:`streamsets.sdk.ControlHub.duplicate_pipeline` method.
This will take an already-existing pipeline and duplicate it the number of times specified:

.. code-block:: python

    pipeline = sch.pipelines.get(commit_id='6889df89-7aaa-4e10-9f26-bdf16af4c0db:admin')
    sch.duplicate_pipeline(pipeline, number_of_copies=2)

**Output:**

.. code-block:: python

    [<Pipeline (pipeline_id=2a385de6-156e-4769-be48-3363fea582d1:admin,
                commit_id=9b0bba1f-6b27-4905-98fa-77b7ce5b57da:admin,
                name=dev copy1,
                version=1-DRAFT)>,
     <Pipeline (pipeline_id=12ae8e89-8d83-4315-9239-a64981fcdbf3:admin,
                commit_id=3fccbdf6-fdbd-418b-be7c-7afec4da8078:admin,
                name=dev copy2,
                version=1-DRAFT)>]

