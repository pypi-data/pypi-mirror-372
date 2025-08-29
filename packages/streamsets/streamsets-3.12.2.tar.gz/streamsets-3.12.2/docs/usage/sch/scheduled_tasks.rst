Scheduled Tasks
===============
|
A scheduled task in Control Hub is an action on a job or report that is set to run periodically, at the frequency
specified.

Creating a new Scheduled Task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new :py:class:`streamsets.sdk.sch_models.ScheduledTask` instance, use :py:meth:`streamsets.sdk.ControlHub.get_scheduled_task_builder`
to add a :py:class:`streamsets.sdk.sch_models.Job` or :py:class:`streamsets.sdk.sch_models.Report` to the task.

.. code-block:: python

    job = sch.jobs[0]
    task = sch.get_scheduled_task_builder().build(task_object=job,
                                                  action='START',
                                                  name='Task for job {}'.format(job.job_name),
                                                  description='Scheduled task for job {}'.format(job.job_name),
                                                  cron_expression='0/1 * 1/1 * ? *',
                                                  time_zone='UTC',
                                                  status='RUNNING')
    sch.add_scheduled_task(task)

Getting an existing Scheduled Task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To retrieve a particular Scheduled Task that already exists in Control Hub, you can filter the available
:py:class:`streamsets.sdk.sch_models.ScheduledTasks` from the :py:class:`streamsets.sdk.ControlHub` object:

.. code-block:: python

    sch.scheduled_tasks
    task = sch.scheduled_tasks.get(name='Start Job for Scheduler')
    task.runs

**Output:**

.. code-block:: python

    # sch.scheduled_tasks
    [<ScheduledTask (id=01efd30a-b462-4694-aff7-1148b04b3c89, name=Stop task for job test_simple_job, status=RUNNING)>,
     <ScheduledTask (id=2dacc46b-fcb3-4e9b-bd72-4023f6c7fe51, name=Start Job for Scheduler, status=PAUSED)>,
     <ScheduledTask (id=41ebbbe2-675a-4300-8027-f6e12eafb53f, name=Job for dev to trash, status=PAUSED)>,
     <ScheduledTask (id=4a82cdc1-7eb1-422e-ac46-fb721ac84354, name=Stop Job for Scheduler, status=RUNNING)>,
     <ScheduledTask (id=ee34fe1c-0991-4509-9a4d-6153c3865faa, name=Stop task for job test_simple_job, status=RUNNING)>]

    # task.runs
    [<ScheduledTaskRun (id=38b82a06-9947-4205-a462-560d7029a182, scheduledTime=1553725200000)>,
     <ScheduledTaskRun (id=b300117e-c339-498b-8393-b8deb69c0f0d, scheduledTime=1553725080000)>,
     <ScheduledTaskRun (id=e7048225-b3d5-4788-9620-c709f24a02aa, scheduledTime=1553725140000)>,
     <ScheduledTaskRun (id=ff1874ac-f0c9-4c72-beec-db397f7b02de, scheduledTime=1553725260000)>]

Operating on an existing Scheduled Task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've obtained the desired Scheduled Task from Control Hub, a number of options can be taken on it. These include
``resume``, ``pause``, ``kill``, and ``delete``. Continuing on from our example above:

.. code-block:: python

    task
    task.resume()
    task.pause()
    task.kill()
    task.delete()

**Output:**

.. code-block:: python

    # task
    <ScheduledTask (id=2dacc46b-fcb3-4e9b-bd72-4023f6c7fe51, name=Start Job for Scheduler, status=PAUSED)>

    # task.resume()
    <ScheduledTask (id=2dacc46b-fcb3-4e9b-bd72-4023f6c7fe51, name=Start Job for Scheduler, status=RUNNING)>

    # task.pause()
    <ScheduledTask (id=2dacc46b-fcb3-4e9b-bd72-4023f6c7fe51, name=Start Job for Scheduler, status=PAUSED)>

    # task.kill()
    <ScheduledTask (id=2dacc46b-fcb3-4e9b-bd72-4023f6c7fe51, name=Start Job for Scheduler, status=KILLED)>

    # task.delete()
    <ScheduledTask (id=2dacc46b-fcb3-4e9b-bd72-4023f6c7fe51, name=Start Job for Scheduler, status=DELETED)>

