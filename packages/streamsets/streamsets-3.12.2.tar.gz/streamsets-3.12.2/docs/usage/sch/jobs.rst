Jobs
====
|
A job defines the pipeline to run and the execution engine that runs the pipeline. The SDK enables you to interact with
jobs on a Control Hub instance including creating a job, deleting a job, starting a job, stopping a job, retrieving
a job's metrics, and more.

Creating a Job
~~~~~~~~~~~~~~

To create a new :py:class:`streamsets.sdk.sch_models.Job` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.JobBuilder` class. Use the :py:meth:`streamsets.sdk.ControlHub.get_job_builder`
method to instantiate the builder object:

.. code-block:: python

    job_builder = sch.get_job_builder()

Next, retrieve the :py:class:`streamsets.sdk.sch_models.Pipeline` object that you wish to create to the job for,
pass it to the :py:meth:`streamsets.sdk.sch_models.JobBuilder.build` method, and pass the resulting job object to the
:py:meth:`streamsets.sdk.ControlHub.add_job` method:

.. code-block:: python

    pipeline = sch.pipelines.get(name='Test Pipeline')
    job = job_builder.build('job name', pipeline=pipeline)
    sch.add_job(job)

Creating a Job with a particular pipeline version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a job with a specific version of a pipeline, you can pass a specific pipeline commit to the
:py:meth:`streamsets.sdk.sch_models.JobBuilder.build` method. Simply retrieve the desired :py:class:`streamsets.sdk.sch_models.PipelineCommit`
instance from the pipeline you're creating the job for:

.. code-block:: python

    job_builder = sch.get_job_builder()
    pipeline = sch.pipelines.get(name='Test Pipeline')
    pipeline_commit = pipeline.commits.get(version='1')
    job = job_builder.build('job name', pipeline=pipeline, pipeline_commit=pipeline_commit)
    sch.add_job(job)

Upgrading a Job
~~~~~~~~~~~~~~~

When a job uses a pipeline that gets updated, it is necessary to upgrade the job to make sure the latest version of the
pipeline is being used in the job. To upgrade one or more jobs to the corresponding latest pipeline version, you can use
the :py:meth:`streamsets.sdk.ControlHub.upgrade_job` method:

.. code-block:: python

    # Get all job instances that use the pipeline version tagged with the 'v1' commit label
    jobs = sch.jobs.get_all(pipeline_commit_label='v1')
    sch.upgrade_job(*jobs)

Updating a Job with a different pipeline version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A job can also be updated to use an entirely different pipeline or pipeline version. Set the :py:attr:`streamsets.sdk.sch_models.Job.commit`
attribute of the :py:class:`streamsets.sdk.sch_models.Job` instance to point to the new pipeline commit, and then pass
the updated :py:class:`streamsets.sdk.sch_models.Job` instance to the :py:meth:`streamsets.sdk.ControlHub.update_job`
method:

.. code-block:: python

    job = sch.jobs.get(pipeline_commit_label='v2')
    pipeline = sch.pipelines.get(name='Test Pipeline')
    pipeline_commit = pipeline.commits.get(version='1')
    job.commit = pipeline_commit
    sch.update_job(job)

Duplicating a Job
~~~~~~~~~~~~~~~~~

The SDK also allows for explicitly duplicating an existing job in Control Hub. Simply retrieve the :py:class:`streamsets.sdk.sch_models.Job`
instance that you want to duplicate, and pass it to the :py:meth:`streamsets.sdk.ControlHub.duplicate_job` method
along with the number of copies to create:

.. code-block:: python

    job = sch.jobs.get(job_id='6889df89-7aaa-4e10-9f26-bdf16af4c0db:admin')
    sch.duplicate_job(job, number_of_copies=2)

**Output:**

.. code-block:: python

    [<Job (job_id=e52c4157-2aec-4b7c-b875-8244d5dc220b:admin, job_name=Job for dev copy1)>,
     <Job (job_id=c0307b6e-2eee-44e3-b8b1-9600e25a30b7:admin, job_name=Job for dev copy2)>]

Importing Jobs
~~~~~~~~~~~~~~

Jobs can also be imported directly in the SDK. To import one or more jobs from a compressed archive, you can use the
:py:meth:`streamsets.sdk.ControlHub.import_jobs` method, passing in the compressed archive to the method. This will
return a :py:class:`streamsets.sdk.utils.SeekableList` of the :py:class:`streamsets.sdk.sch_models.Job` objects that
were imported:

.. code-block:: python

    # Open a compressed archive for reading, and then pass it into the import_jobs method
    with open('jobs.zip', 'rb') as jobs_file:
        jobs = sch.import_jobs(archive=jobs_file)

Exporting Jobs
~~~~~~~~~~~~~~

Similarly, jobs can also be exported from Control Hub directly in the SDK. To export one or more jobs to a compressed
archive, use the :py:meth:`streamsets.sdk.ControlHub.export_jobs` method after retrieving the :py:class:`streamsets.sdk.sch_models.Job`
object(s) you wish to export:

.. code-block:: python

    # Retrieve the Job objects to export - all jobs on Control Hub, in this example
    jobs = sch.jobs
    jobs_file_data = sch.export_jobs(jobs)

    # Open an archive file for writing, and write out the exported job data
    with open('jobs.zip', 'wb') as jobs_file:
        jobs_file.write(jobs_file_data)

Resetting offsets
~~~~~~~~~~~~~~~~~

Jobs maintain offsets to keep track of the most-recently processed data before the job was stopped. It is sometimes
desirable, or necessary, to reset the offset of a particular job. To reset offsets for one or more jobs,
use the :py:meth:`streamsets.sdk.ControlHub.reset_origin` method after retrieving the :py:class:`streamsets.sdk.sch_models.Job`
instance(s) you wish to reset:

.. code-block:: python

    # Get all jobs available from Control Hub, then reset each of their origins
    jobs = sch.jobs
    sch.reset_origin(*jobs)

Retrieving Offsets
~~~~~~~~~~~~~~~~~~

A job's current offsets can also be retrieved via the SDK. To retrieve the current offsets of a job, reference the
:py:attr:`streamsets.sdk.sch_models.JobStatus.offsets` attribute of the job's :py:attr:`streamsets.sdk.ControlHub.Job.current_status`. This will return a
:py:class:`streamsets.sdk.sch_models.JobOffset` object

.. code-block:: python

   job = sch.job.get(name='job name')
   job.current_status.offsets

**Output:**

.. code-block:: python

   [<JobOffset (sdc_id=0501dc93-8634-11e9-99f3-97919257db3c, pipeline_id=896197a7-9639-4575-9784-260f1dc46fbc:admin)>]

To retrieve offsets from a particular job run, you can reference the :py:attr:`streamsets.sdk.sch_models.JobStatus.offsets`
attribute of a job's :py:attr:`streamsets.sdk.ControlHub.Job.history` object:

.. code-block:: python

   # Get the most recent run (JobStatus object) from the job's history
   job_status = job.history[0]
   job_status.offsets

**Output:**

.. code-block:: python

   [<JobOffset (sdc_id=0501dc93-8634-11e9-99f3-97919257db3c, pipeline_id=896197a7-9639-4575-9784-260f1dc46fbc:admin)>]

Uploading offsets
~~~~~~~~~~~~~~~~~

It's also possible to upload a job's offset. For example, if you create a second job that reads the
same origin data as an existing job, but you want to ensure both to start with the latest offset, you could upload the
offset to the newly-created job. To upload offsets for a job use the
:py:meth:`streamsets.sdk.ControlHub.upload_offset` method:

.. code-block:: python

    job = sch.jobs.get(name='job name')

    with open('offset.json') as offset_file:
        sch.upload_offset(job, offset_file=offset_file)

The :py:meth:`streamsets.sdk.ControlHub.upload_offset` method can also be used to upload an offset in raw JSON format:

.. code-block:: python

    offset_json = {"version" : 2,
                   "offsets" : {"$com.streamsets.datacollector.pollsource.offset$" : None}}
    sch.upload_offset(job, offset_json=offset_json)

Retrieving Job Status History
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieving a given job's history can also be done from the SDK. Simply retrieve the :py:class:`streamsets.sdk.sch_models.Job`
instance in question from Control Hub and reference its :py:attr:`streamsets.sdk.sch_models.Job.history`
attribute. This will show the execution history for the job all contained within a
:py:class:`streamsets.sdk.sch_models.JobStatus` object:

.. code-block:: python

    job = sch.jobs[0]
    job.history

**Output:**

.. code-block:: python

    [<JobStatus (status=INACTIVE, start_time=1585923912290, finish_time=1585923935759, run_count=2)>,
     <JobStatus (status=INACTIVE, start_time=1585923875846, finish_time=1585923897766, run_count=1)>]

Retrieving Run Events from Job History
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can introspect on an individual :py:class:`streamsets.sdk.sch_models.JobStatus` object within a job to see the
run events for it. The run events correspond to the events that occurred during that execution, like the job activating
or deactivating:

.. code-block:: python

    # Get the most recent run (JobStatus object) from the job's history
    job_status = job.history[0]
    job_status.run_history

**Output:**

.. code-block:: python

    [<JobRunEvent (user=admin@admin, time=1560367534056, status=ACTIVATING)>,
     <JobRunEvent (user=admin@admin, time=1560367540929, status=DEACTIVATING)>,
     <JobRunEvent (user=None, time=1560367537771, status=DEACTIVATING)>,
     <JobRunEvent (user=None, time=1560367537814, status=DEACTIVATING)>]

Metrics
~~~~~~~

To access metrics for a job, reference the :py:attr:`streamsets.sdk.sch_models.Job.metrics` attribute of a
:py:class:`streamsets.sdk.sch_models.Job` instance. This will return a :py:class:`streamsets.sdk.utils.SeekableList` of
:py:class:`streamsets.sdk.sch_models.JobMetrics` objects that are in reverse chronological order (newest first):

.. code-block:: python

    job = sch.jobs.get(job_name='job name')
    job.metrics

**Output:**

.. code-block:: python

    [<JobMetrics (run_count=5, input_count=3204, output_count=3204, total_error_count=0)>,
     <JobMetrics (run_count=4, input_count=24740, output_count=24740, total_error_count=0)>,
     <JobMetrics (run_count=3, input_count=9960, output_count=9960, total_error_count=0)>,
     <JobMetrics (run_count=2, input_count=9564, output_count=9564, total_error_count=0)>,
     <JobMetrics (run_count=1, input_count=792, output_count=792, total_error_count=0)>]

We can also reference the :py:attr:`streamsets.sdk.sch_models.Job.history` attribute of a :py:class:`streamsets.sdk.sch_models.Job`
instance to figure out which job run we might be interested in. For example, if we wanted to know which job run executed
at Apr 01 2021 16:39:48 GMT (unix-timestamp '1617295188217') and get the metrics for it, we could use the following
steps:

.. code-block:: python

    job.history.get(start_time=1617295188217)

**Output:**

.. code-block:: python

    <JobStatus (status=INACTIVE, start_time=1617295188217, finish_time=1617295209406, run_count=2)>

|
This was run_count 2, so now we know which run_count to reference for this run's metrics

.. code-block:: python

    job.metrics.get(run_count=2)

**Output:**

.. code-block:: python

    <JobMetrics (run_count=2, input_count=9564, output_count=9564, total_error_count=0)>

Time Series Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When time series analysis is enabled for a job, you can check the time series metrics from the SDK directly. The SDK
provides a breakdown of :py:attr:`streamsets.sdk.sch_models.JobTimeSeriesMetrics.input_records`,
:py:attr:`streamsets.sdk.sch_models.JobTimeSeriesMetrics.output_records`, and
:py:attr:`streamsets.sdk.sch_models.JobTimeSeriesMetrics.error_records`.

To access time series metrics for a job, use the :py:meth:`streamsets.sdk.sch_models.Job.time_series_metrics` method
and pass in the ``metric_type`` you're interested in. Available options are:

* ``'Record Count Time Series'`` - Total count of each category of records (input, output, error) for the given time frame.
* ``'Record Throughput Time Series'`` - The number of records of each category of records (input, output, error) processed, per second, for the given time frame.
* ``'Batch Throughput Time Series'`` - The number of record batches processed per second for the given time frame.
* ``'Stage Batch Processing Timer seconds'`` - The amount of time it took to process a record batch in each stage of the job's pipeline.

.. code-block:: python

    # Get the number of records processed per second for a job
    job_time_series_metrics = job.time_series_metrics(metric_type='Record Throughput Time Series')
    job_time_series_metrics

    # Drill down further to just the input_records
    job_time_series_metrics.input_records

    # Drill down even further and look at just the time_series metrics values of the input_records
    job_time_series_metrics.input_records.time_series

**Output:**

.. code-block:: python

    # job_time_series_metrics
    <JobTimeSeriesMetrics (
    input_records=<JobTimeSeriesMetric (name=pipeline_batchInputRecords_meter,
                                        time_series={'2019-06-24T19:35:01.34Z': 182000.0,
                                                     '2019-06-24T19:36:03.273Z': 242000.0,
                                                     '2019-06-24T19:37:05.202Z': 303000.0,
                                                     '2019-06-24T19:38:07.135Z': 363000.0,
                                                     '2019-06-24T19:39:09.065Z': 424000.0})>,
    output_records=<JobTimeSeriesMetric (name=pipeline_batchOutputRecords_meter,
                                         time_series={'2019-06-24T19:35:01.34Z': 182000.0,
                                                      '2019-06-24T19:36:03.273Z': 242000.0,
                                                      '2019-06-24T19:37:05.202Z': 303000.0,
                                                      '2019-06-24T19:38:07.135Z': 363000.0,
                                                      '2019-06-24T19:39:09.065Z': 424000.0})>,
    error_records=<JobTimeSeriesMetric (name=pipeline_batchErrorRecords_meter,
                                        time_series={'2019-06-24T19:35:01.34Z': 0.0,
                                                     '2019-06-24T19:36:03.273Z': 0.0,
                                                     '2019-06-24T19:37:05.202Z': 0.0,
                                                     '2019-06-24T19:38:07.135Z': 0.0,
                                                     '2019-06-24T19:39:09.065Z': 0.0})>)>

    # job_time_series_metrics.input_records
    <JobTimeSeriesMetric (name=pipeline_batchInputRecords_meter, time_series={'2019-06-24T19:35:01.34Z': 182000.0,
                                                                              '2019-06-24T19:36:03.273Z': 242000.0,
                                                                              '2019-06-24T19:37:05.202Z': 303000.0,
                                                                              '2019-06-24T19:38:07.135Z': 363000.0,
                                                                              '2019-06-24T19:39:09.065Z': 424000.0})>

    # job_time_series_metrics.input_records.time_series
    {'2019-06-24T19:35:01.34Z': 182000.0,
     '2019-06-24T19:36:03.273Z': 242000.0,
     '2019-06-24T19:37:05.202Z': 303000.0,
     '2019-06-24T19:38:07.135Z': 363000.0,
     '2019-06-24T19:39:09.065Z': 424000.0}

By default, the :py:meth:`streamsets.sdk.sch_models.Job.time_series_metrics` method will gather metrics for the last five
minutes, but the length of time can be modified by passing in ``time_filter_condition`` arguments. The available
``time_filter_condition`` values can be found in Control Hub's API documentation:

.. code-block:: python

    # Get 'Record Throughput Time Series' metrics from a job for the last 15 minutes
    job_time_series_metrics = job.time_series_metrics(metric_type='Record Throughput Time Series', time_filter_condition='LAST_15M')

    # Get 'Record Count Time Series' metrics from a job for the last hour, 6 hours, 12 hours, and then 24 hours
    job_time_series_metrics = job.time_series_metrics(metric_type='Record Count Time Series', time_filter_condition='LAST_1H')
    job_time_series_metrics = job.time_series_metrics(metric_type='Record Count Time Series', time_filter_condition='LAST_6H')
    job_time_series_metrics = job.time_series_metrics(metric_type='Record Count Time Series', time_filter_condition='LAST_12H')
    job_time_series_metrics = job.time_series_metrics(metric_type='Record Count Time Series', time_filter_condition='LAST_24H')

    # Get 'Batch Throughput Time Series' metrics from a job for the last 2 days, 7 days, and then 30 days
    job_time_series_metrics = job.time_series_metrics(metric_type='Batch Throughput Time Series', time_filter_condition='LAST_2D')
    job_time_series_metrics = job.time_series_metrics(metric_type='Batch Throughput Time Series', time_filter_condition='LAST_7D')
    job_time_series_metrics = job.time_series_metrics(metric_type='Batch Throughput Time Series', time_filter_condition='LAST_30D')

Balancing Data Collector instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Control Hub allows jobs to be balanced across Data Collector instances that are tagged appropriately for the jobs in
question. To balance all jobs running on specific Data Collectors, you can use the
:py:meth:`streamsets.sdk.ControlHub.balance_data_collectors` method after retrieving the specific :py:class:`streamsets.sdk.DataCollector`
instance(s) that you want to balance:

.. code-block:: python

    # Retrieve the Data Collector instances to be balanced - all Data Collector instances, in this example
    data_collectors = sch.data_collectors
    sch.balance_data_collectors(data_collectors)

