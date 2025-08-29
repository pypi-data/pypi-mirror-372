Job Tags
========
|
A job tag identifies similar jobs or job templates, and can be used to easily search and filter jobs and job templates.

Creating a job with tags
~~~~~~~~~~~~~~~~~~~~~~~~

To specify tags for a :py:class:`streamsets.sdk.sch_models.Job` instance at creation time, you need to supply the
desired tags at the time :py:meth:`streamsets.sdk.sch_models.JobBuilder.build` is called for the pipeline being created:

.. code-block:: python

    job_builder = sch.get_job_builder()
    pipeline = sch.pipelines.get(id=<pipeline id>)
    # Create a list of tags to supply to the builder
    tags = ['test/dev', 'test']
    job = job_builder.build(job_name='Test job with tags', pipeline=pipeline, tags=tags)
    sch.add_job(job)
    job.tags

**Output:**

.. code-block:: python

    # job.tags
    [<Tag (tag=test/dev)>,
     <Tag (tag=test)>]

Fetching jobs using job tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Job tags can be used to search and filter through the available jobs and job templates on Control Hub. To fetch a
particular job or jobs that use a specific job tag, you can supply it via the ``job_tag`` parameter:

.. code-block:: python

    sch.jobs.get_all(job_tag='test:admin')

**Output:**

.. code-block:: python

    [<Job (job_id=93084250-ef6f-4c0a-b6f8-aff54f905739:admin, job_name=Test job with tags)>]

.. note::
  The ``job_tag`` you provide is expected to be in a '<tag_name>:<organization>' format.

Adding tags to an existing job
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also add new tags to a :py:class:`streamsets.sdk.sch_models.Job` instance via the
:py:meth:`streamsets.sdk.sch_models.Job.add_tag` method by passing in one or more :py:obj:`string` objects to add:

.. code-block:: python

    job = sch.jobs.get(job_id=<job_id>)
    job.add_tag('prod/dev', 'prod')
    sch.update_job(job)
    job.tags

**Output:**

.. code-block:: python

    # job.tags
    [<Tag (tag=test/dev)>,
     <Tag (tag=test)>,
     <Tag (tag=prod/dev)>,
     <Tag (tag=prod)>]

Removing existing tags for a job
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Existing tags can also be removed from a :py:class:`streamsets.sdk.sch_models.Job` instance via the
:py:meth:`streamsets.sdk.sch_models.Job.remove_tag` method by passing in one or more :py:obj:`string` objects to remove:

.. code-block:: python

    job = sch.jobs.get(job_id=<job_id>)
    job.remove_tag('test', 'test/dev')
    sch.update_job(job)
    job.tags

**Output:**

.. code-block:: python

    # job.tags
    [<Tag (tag=prod/dev)>,
     <Tag (tag=prod)>]]