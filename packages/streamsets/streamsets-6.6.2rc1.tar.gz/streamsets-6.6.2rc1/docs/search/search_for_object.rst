.. _search_for_objects:

SAQL
====

SAQL (StreamSets Advanced Query Language) allows searching for a specific object or set of
objects belonging to your organization.

At this time, the SDK supports searching for pipelines, fragments, and job instances. StreamSets SDK will implement
search for additional object types in future releases.

Each searchable object type includes a fixed set of properties that you create search conditions for. For example, you
can search for pipelines by the Commit Message property, or search for jobs by the Failover property.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Search/AdvancedSearch_title.html>`_
for search functionality.

Search Use Cases
~~~~~~~~~~~~~~~~
You can search for objects to address the following common use cases:

Find similar pipelines to help with pipeline development
````````````````````````````````````````````````````````
As a new pipeline developer, you want to explore pipelines created by other developers to solve a problem with your own pipeline.
You search for pipelines that contain the string ``'Snowflake'`` in the name and that have the label ``'WestDataCenter'``.

Find jobs that have encountered errors and that are owned by multiple teams
```````````````````````````````````````````````````````````````````````````
As a manager, you want to view a list of running jobs that have encountered errors that are owned by your three development teams. Each development team assigns a unique engine label to the jobs that they run: tools, adaptors, or platform.
You search for jobs that are assigned the tools, adaptors, or platform engine label and that have an ``INACTIVE_ERROR`` status.

Find a specific pipeline version
````````````````````````````````
As a pipeline developer, you want to quickly find version 5 of the SocialFeedsDataflow pipeline. It's an older version of the pipeline, and you don't want to spend time opening the most recent version of the pipeline in the pipeline canvas and then selecting the older version.
You search for a pipeline with the name ``'SocialFeedsDataflow'`` where the pipeline version is ``'5'``.

Searching for specific objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To search for objects, you define the conditions for your search.
From the Platform UI, searching for an object can be done as shown below:

.. image:: ../_static/images/search/Search_Advanced.png

|
|

In the SDK you can define search conditions for the following objects:

Pipelines
`````````
In the SDK, searching for a pipeline is similar, using the :py:meth:`streamsets.sdk.sch_models.Pipelines.get_all` method.
Supplying a value to the ``search`` parameter will return a :py:class:`streamsets.sdk.utils.SeekableList` of
:py:class:`streamsets.sdk.sch_models.Pipeline` instances that match the search query.

.. code-block:: python

    # Search for pipelines
    query = 'draft==false and engine_type=in=(COLLECTOR,TRANSFORMER) and modified_on>=2022-01001) or label==test or label==write'
    pipelines = sch.pipelines.get_all(search=query)

Pipeline Fragments
``````````````````
Searching for pipeline fragments is very similar to searching for pipelines. You'll still utilize the
:py:meth:`streamsets.sdk.sch_models.Pipelines.get_all` method and ``search`` query parameter, but supply ``fragment==True`` to the method as well.

.. code-block:: python

    # Search for fragments
    query = 'draft==false and engine_type=in=(COLLECTOR,TRANSFORMER) and modified_on>=2022-01001) or label==test or label==write'
    fragments = sch.pipelines.get_all(search=query, fragment=True)

Jobs
````
Searching for a job using the SDK is similar to searching for a pipeline, using the :py:meth:`streamsets.sdk.sch_models.Jobs.get_all` method instead.
Supplying a value to the ``search`` parameter will return
a :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Job` instances that match the search query.

.. code-block:: python

    # Search for jobs
    query = 'name=="*even_jobs*"'
    jobs = sch.jobs.get_all(search=query)

Job Templates
````
Searching for job templates is very similar to searching for jobs. You'll still utilize the
:py:meth:`streamsets.sdk.sch_models.Jobs.get_all` method and ``search`` query parameter, but supply ``job_template==True`` to the method as well.

.. code-block:: python

    # Search for jobs
    query = 'name=="*even_templates*"'
    job_templates = sch.jobs.get_all(search=query, job_template=True)

.. warning::
    When supplying the ``search`` parameter the ``order_by`` parameter takes in "MODIFIED_ON" as opposed to
    "LAST_MODIFIED_ON"

    .. code-block:: python

        jobs = sch.jobs.get_all(search=query, order_by="MODIFIED_ON")
        pipelines = sch.pipelines.get_all(search=query, order_by="MODIFIED_ON")

Job Statuses
````
Searching for a Job Status using the SDK entails calling the :py:meth:`streamsets.sdk.sch_models.JobStatuses.get_all` method.
This entails calling the :py:attr:`streamsets.sdk.sch_models.Job.job_history` attribute and supplying a value to the ``search`` parameter within the :py:meth:`streamsets.sdk.sch_models.JobStatuses.get_all` method.
This will return a :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.JobStatus` instances that match the search query.

.. code-block:: python

    query = "color ==GRAY"
    job = sch.jobs[0]
    # Search for Job Statuses
    gray_job_statuses = job.job_history.get_all(search=query)

.. note::
    The acceptable values that you can search by are ``id``, ``previous_id``, ``pipeline_commit_id``, ``run_count``, ``color``, ``status``, ``start_time``, ``finish_time``, ``error_message``, ``input_record_count``, ``output_record_count``, ``error_record_count`` and ``current_retry_count``.
