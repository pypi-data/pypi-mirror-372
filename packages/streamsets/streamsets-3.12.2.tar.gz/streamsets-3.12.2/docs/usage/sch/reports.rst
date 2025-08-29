Reports
=======
|
Interacting with reports and report definitions allows you to define a custom data delivery report that
provides data processing metrics for a given job or topology in Control Hub.

Creating a Report Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A report definition can be built and added to Control Hub using the
:py:class:`streamsets.sdk.sch_models.ReportDefinitionBuilder` class. Use the
:py:meth:`streamsets.sdk.ControlHub.get_report_definition_builder` method to instantiate the builder object:

.. code-block:: python

    report_definition_builder = sch.get_report_definition_builder()
    # Set the report generation time frame for last 30 minutes.
    report_definition_builder.set_data_retrieval_period(start_time='${time:now() - 30 * MINUTES}', end_time='${time:now()}')

    # Add resources to the Report.
    job = sch.jobs.get(job_name='name')
    topology = sch.topologies.get(topology_name='name')
    report_definition_builder.add_report_resource(job)
    report_definition_builder.add_report_resource(topology)

    # Build and publish.
    report_definition = report_definition_builder.build(name='from sdk')
    sch.add_report_definition(report_definition)

Creating Report Definitions using absolute time range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also create a report definition for a fixed, absolute time range using the same arguments and methods as above.
Simply specify the timestamp of both ``start_time`` and ``end_time`` in milliseconds:

.. code-block:: python

    import datetime
    start_time = datetime.datetime(2019, 4, 1).timestamp() * 1000
    end_time = datetime.datetime(2019, 4, 10).timestamp() * 1000
    report_definition_builder.set_data_retrieval_period(start_time=start_time, end_time=end_time)

Generating a Report
~~~~~~~~~~~~~~~~~~~

Once you have a report definition created for a particular job and/or topology, you can then trigger the generation
of a data delivery report for that definition by using the :py:meth:`streamsets.sdk.sch_models.ReportDefinition.generate_report`
method:

.. code-block:: python

    report_defintion = sch.report_definitions.get(name='from sdk')
    report_command = report_defintion.generate_report()

    report_command.report

    # After the report is generated
    report_command.report

**Output:**

.. code-block:: python

    # report_command.report
    Report is still being generated...

    # report_command.report
    <Report (id=13114c45-15ce-44d1-8ff5-bc5ba73f5b8a:admin, name=from sdk at 04-12-2019 18:38:00 UTC)>

Getting existing Report Definitions and Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is also possible to retrieve existing report definitions and their corresponding reports. Simply
reference the ``report_definitions`` attribute of your :py:class:`streamsets.sdk.ControlHub` instance to get a list of
all :py:class:`streamsets.sdk.sch_models.ReportDefinition` objects:

.. code-block:: python

    sch.report_definitions

**Output:**

.. code-block:: python

    [<ReportDefinition (id=c8982001-41f3-4581-8fb0-dcabc5fd7115:admin, name=Report for test job)>,
     <ReportDefinition (id=8cca181f-b9a2-4489-b493-accf128e9901:admin, name=Report for test topology)>,
     <ReportDefinition (id=4c7dccf1-30a8-4b81-9463-7723e0697d62:admin, name=from sdk)>]

You can also further filter and refine which report definition you're interested in with attributes like ``name`` or
``id``:

.. code-block:: python

    # Get Report Definitions
    sch.report_definitions.get(name='from sdk')

**Output:**

.. code-block:: python

    <ReportDefinition (id=4c7dccf1-30a8-4b81-9463-7723e0697d62:admin, name=from sdk)>

Once you have obtained the report definition object you're interested in, you can view additional data associated with
that definition - such as the :py:attr:`streamsets.sdk.sch_models.ReportDefinition.report_resources` attributed to it,
or the :py:attr:`streamsets.sdk.sch_models.ReportDefinition.reports` the definition has already generated:

.. code-block:: python

    # Get Report Resources
    sch.report_definitions.get(name='from sdk').report_resources
    [<ReportResource (resource_type=JOB, resource_id=fa9517c8-c93d-432e-b880-9c2d2d1c5dfe:admin)>,
     <ReportResource (resource_type=TOPOLOGY, resource_id=b124dedf-cbc9-4632-a765-8fc59b9636ab:admin)>]

    # Get Reports
    sch.report_definitions.get(name='from sdk').reports

    # These properties can also be referenced directly from the object itself
    report_definition = sch.report_definitions.get(name='from sdk')
    report_definition.report_resources
    report_definition.reports

**Output:**

.. code-block:: python

    # sch.report_definitions.get(name='from sdk').report_resources
    [<ReportResource (resource_type=JOB, resource_id=fa9517c8-c93d-432e-b880-9c2d2d1c5dfe:admin)>,
     <ReportResource (resource_type=TOPOLOGY, resource_id=b124dedf-cbc9-4632-a765-8fc59b9636ab:admin)>]

    # sch.report_definitions.get(name='from sdk').reports
    [<Report (id=13114c45-15ce-44d1-8ff5-bc5ba73f5b8a:admin, name=from sdk at 04-12-2019 18:38:00 UTC)>,
     <Report (id=663490aa-b413-460d-8b0d-38b52592cfb2:admin, name=from sdk at 04-12-2019 18:31:00 UTC)>]

    # report_definition.report_resources
    [<ReportResource (resource_type=JOB, resource_id=fa9517c8-c93d-432e-b880-9c2d2d1c5dfe:admin)>,
     <ReportResource (resource_type=TOPOLOGY, resource_id=b124dedf-cbc9-4632-a765-8fc59b9636ab:admin)>]

    # report_definition.reports
    [<Report (id=13114c45-15ce-44d1-8ff5-bc5ba73f5b8a:admin, name=from sdk at 04-12-2019 18:38:00 UTC)>,
     <Report (id=663490aa-b413-460d-8b0d-38b52592cfb2:admin, name=from sdk at 04-12-2019 18:31:00 UTC)>]

Downloading existing Reports as PDF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reports generated by a report definition are stored in PDF format, and can be downloaded and modified as needed.
Simply obtain the report definition you're interested in, identify which report you wish to download, and then use the
:py:meth:`streamsets.sdk.sch_models.Report.download` method:

.. code-block:: python

    report_defintion = sch.report_definitions.get(name='from sdk')
    # Show the reports in the report definition
    report_definition.reports

    # Download the report, store it in report_content
    report_content = report_defintion.reports[0].download()

    # Write the report's contents to a file
    with open('report.pdf', 'wb') as f:
        f.write(report_content)

**Output:**

.. code-block:: python

    # report_definition.reports
    [<Report (id=13114c45-15ce-44d1-8ff5-bc5ba73f5b8a:admin, name=from sdk at 04-12-2019 18:38:00 UTC)>,
     <Report (id=663490aa-b413-460d-8b0d-38b52592cfb2:admin, name=from sdk at 04-12-2019 18:31:00 UTC)>]

Updating an existing Report Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updating an existing report definition is similar to creating a new report definition for the first time. It makes use
of the :py:class:`streamsets.sdk.sch_models.ReportDefinitionBuilder` class to import the existing report definition
object first, which then allows the report definition to be modified. Once the definition has been modified as desired,
the :py:meth:`streamsets.sdk.sch_models.ReportDefinitionBuilder.build` method is used to construct the
:py:class:`streamsets.sdk.sch_models.ReportDefinition` which can then be passed to Control Hub via the
:py:meth:`streamsets.sdk.ControlHub.update_report_definition` method:

.. code-block:: python

    report_definition_builder = sch.get_report_definition_builder()
    report_definition = sch.report_definitions.get(name='from sdk')

    # Import Report Definition into Report Definition Builder.
    report_definition_builder.import_report_definition(report_definition)

    # Remove topology from resources
    topology = sch.topologies.get(topology_id='topology_id=2c8a398c-775f-45cf-a338-5425c47b7084:admin')
    report_definition_builder.remove_report_resource(topology)

    # Add job to resources
    job = sch.jobs.get(job_name='another job')
    report_definition_builder.add_report_resource(job)

    # Update time range from last 30 minutes to last 2 days
    report_definition_builder.set_data_retrieval_period(start_time='${time:now() - 2 * DAYS}', end_time='${time:now()}')
    sch.update_report_definition(report_defintion)

Scheduling Report generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reports can also be generated at a set internal for a particular report definition. Periodic report generation is
handled as a scheduled task, and requires a cron expression to be specified for the interval. To schedule periodic
report generation, retrieve the :py:class:`streamsets.sdk.sch_models.ReportDefinition` object you wish to schedule
generation for and pass it into the :py:meth:`streamsets.sdk.sch_models.ScheduledTaskBuilder.build` method:

.. code-block:: python

    # Get the report definition to be scheduled
    report_def = sch.report_definitions.get(name='from sdk')

    # Instantiate a ScheduledTaskBuilder, and build the scheduled task with the report_def (from above)
    # as the task_object
    task = sch.get_scheduled_task_builder().build(task_object=report_def,
                                                  action='START',
                                                  name='Task for Report {}'.format(report_def.name),
                                                  cron_expression='0/1 * 1/1 * ? *',
                                                  time_zone='UTC')

    # Publish the scheduled task (built above) to Control Hub
    sch.add_scheduled_task(task)


