Preview and test run
====================

Previewing a pipeline
~~~~~~~~~~~~~~~~~~~~~

To preview a Control Hub pipeline, you can use the :py:meth:`streamsets.sdk.ControlHub.run_pipeline_preview` method
which will return the command's output. This provides a list of :py:class:`streamsets.sdk.sdc_models.Record` objects
that can be further introspected upon.

.. code-block:: python

    preview_command = sch.run_pipeline_preview(pipeline)
    preview = preview_command.preview
    preview[dev_data_generator].output

**Output:**

.. code-block:: python

    [<Record (field={'': '5e9c7f3f-b553-4604-b92b-770fc016cd70'})>,
     <Record (field={'': 'af9eeb58-ff4e-4558-923b-29fbbf94ae8d'})>,
     <Record (field={'': '2b83fada-1eff-45af-bf5c-4c811c5bcc89'})>,
     <Record (field={'': 'aa8c5944-4b95-4aec-9fe3-536d8f0d05f4'})>,
     <Record (field={'': 'a37e6d42-87ab-4736-8a72-107210e05267'})>,
     <Record (field={'': 'dfc4f1f5-854c-4c9e-8324-21505412f4f0'})>,
     <Record (field={'': 'cfd42fc9-4399-44ec-8caf-f2e1d31cd36e'})>,
     <Record (field={'': 'd03ff7c6-0a70-438d-aaeb-01736bddaf52'})>,
     <Record (field={'': 'a4077ac0-4a38-4ef8-8914-ac7f34321ecd'})>,
     <Record (field={'': '708067df-f6ea-4fdb-bfb6-e74a1c002bfc'})>]

Test running a pipeline
~~~~~~~~~~~~~~~~~~~~~~~

To test-run a Control Hub pipeline, use the :py:meth:`streamsets.sdk.ControlHub.test_pipeline_run` method. This will
execute the pipeline on its Authoring Data Collector instance:

.. code-block:: python

    pipeline = sch.pipelines.get(name='Test pipeline')
    test_run_command = sch.test_pipeline_run(pipeline)
    test_run_command.wait_for_status('RUNNING')
    test_run_command.executor_pipeline
    test_run_command.executor_instance
    sch.stop_test_pipeline_run(test_run_command)

**Output:**

.. code-block:: python

    # test_run_command.executor_pipeline
    <Pipeline (id=testRun__48d74ed5-af3c-4196-8696-fba1c6e38673__admin, title=Test pipeline)>

    # test_run_command.executor_instance
    <streamsets.sdk.sdc.DataCollector at 0x10e872fd0>

    # sch.stop_test_pipeline_run(test_run_command)
    <sdk.sdc_api.StopPipelineCommand at 0x10e4cd050>

