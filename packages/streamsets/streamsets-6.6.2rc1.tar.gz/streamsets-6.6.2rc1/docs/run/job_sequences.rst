.. _job_sequences:

Job Sequences
===============
|
A Job Sequence, is a sequence of Jobs to be executed sequentially. The execution of each of these Jobs may or may not be
dependent on the successful execution of the job preceding it.

Creating a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~

In the Platform UI, a Job Sequence can be created from the Sequences section by clicking "Create Sequence" and following the prompts:

.. image:: ../_static/images/run/create_job_sequence.png
|

To create a new Job Sequence and add it via the Platform SDK, you will need to use the :py:class:`streamsets.sdk.sch_models.JobSequenceBuilder` class.
To instantiate a builder instance, use the :py:meth:`streamsets.sdk.ControlHub.get_job_sequence_builder` method.

Once you've instantiated the builder, you can call the :py:meth:`streamsets.sdk.sch_models.JobSequenceBuilder.add_start_condition` method to add a Start Condition along with the ``start_time``, ``end_time``, ``time_zone``, and ``crontab_mask`` parameters.
Next, you will call the :py:meth:`streamsets.sdk.sch_models.JobSequenceBuilder.build` method to create the desired :py:class:`streamsets.sdk.sch_models.JobSequence` instance.

.. code-block:: python

    # Instantiate the JobSequenceBuilder instance
    job_sequence_builder = sch.get_job_sequence_builder()

    # Add a start condition
    job_sequence_builder.add_start_condition(start_time=4200268800, end_time=4200854400, time_zone='UTC', crontab_mask='0/1 * 1/1 * ? *')

    # Build the Job Sequence instance
    job_sequence = job_sequence_builder.build(name='My Job Sequence', description='My Job Sequence Description')

Once you've built your :py:class:`streamsets.sdk.sch_models.JobSequence` instance, you can publish it to Platform using the :py:meth:`streamsets.sdk.ControlHub.publish_job_sequence` method.

.. code-block:: python

    # Publish the Job Sequence to Platform
    sch.publish_job_sequence(job_sequence)

.. Note::
  Publishing your :py:class:`streamsets.sdk.sch_models.JobSequence` instance will update its ``id`` and ``status`` fields respectively.

Adding and Removing Steps From a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new Step in a Job Sequence, one or more jobs must be provided at Step creation time.

You can add Steps into a Job Sequence by clicking 'Add Jobs' from the Sequences section of the Platform UI as seen below:

.. image:: ../_static/images/run/add_jobs_to_job_sequence.png
|

.. image:: ../_static/images/run/add_job_modal.png
|

To add Steps using the Platform SDK, you will need to pass the desired :py:class:`streamsets.sdk.sch_models.Job` instance(s) into the the :py:meth:`streamsets.sdk.sch_models.JobSequence.add_step_with_jobs` method. By default, this will create a Step for every Job that is passed.

In order to add multiple :py:class:`streamsets.sdk.sch_models.Job` instances to the same step - meaning the jobs will execute in parallel - set the ``parallel_jobs`` parameter to ``True``. This will create one Step with all the Jobs that were passed. This is equal to clicking the 'Add jobs to the same step' checkbox in the UI.

.. code-block:: python

    # Add three jobs sequentially to the job_sequence
    job_sequence.add_step_with_jobs([job_one, job_two, job_three])

    # Add three jobs to the same step of the job_sequence
    job_sequence.add_step_with_jobs([job_one, job_two, job_three], parallel_jobs=True)

Similarly, to remove a Step using the Platform SDK, you will need to pass in the desired :py:class:`streamsets.sdk.sch_models.Step` instance into the :py:meth:`streamsets.sdk.sch_models.JobSequence.remove_step` method:

.. code-block:: python

    # Pull the second Step from the Job Sequence
    step = job_sequence.steps.get(step_number=2)

    # Remove Step from the Job Sequence
    job_sequence.remove_step(step)

.. Note::
  Calling the :py:meth:`streamsets.sdk.sch_models.JobSequence.add_step_with_jobs` and :py:meth:`streamsets.sdk.sch_models.JobSequence.remove_step` will commit the changes to Platform in addition to updating the in-memory representation of the JobSequence.

Adding and Removing Jobs From an Existing Step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add Jobs to an existing Step using the Platform SDK, you will need to pass in the desired :py:class:`streamsets.sdk.sch_models.Job` instance(s) into the :py:meth:`streamsets.sdk.sch_models.Step.add_jobs` method:

.. code-block:: python

    # Add three jobs to the Step
    step.add_jobs([job_one, job_two, job_three])

    # Add one job to the Step
    step.add_jobs([job_four])

Similarly, to remove Jobs from an existing Step, you will need to pass in the desired :py:class:`streamsets.sdk.sch_models.Job` instances into the :py:meth:`streamsets.sdk.sch_models.Step.remove_jobs` method:

.. code-block:: python

    # Remove jobs from the Step
    step.remove_jobs(job_one, job_two)

    # Remove one job from the Step
    step.remove_jobs(job_four)

.. Note::
  Calling the :py:meth:`streamsets.sdk.sch_models.Step.add_jobs` and :py:meth:`streamsets.sdk.sch_models.Step.remove_jobs` will commit the changes to Platform in addition to updating the in-memory representation of the JobSequence.

Retrieving Existing Job Sequences
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can view all existing Job Sequences on the Platform by navigating to the Sequences section of the Platform UI as seen below:

.. image:: ../_static/images/run/get_job_sequences.png
|

To retrieve all existing Job Sequences using the Platform SDK, you will need to reference the :py:attr:`streamsets.sdk.ControlHub.job_sequences` attribute.
You can further filter the available Job Sequences on attributes like ``name``, and ``id`` to retrieve specific Job Sequence(s):

.. code-block:: python

    # Retrieve all existing Job Sequences
    all_job_sequences = sch.job_sequences

    # Retrieve all Job Sequences with name Nightly Job Sequence
    nightly_job_sequences = sch.job_sequences.get_all(name='Nightly Job Sequence')

    # Retrieve a Job Sequence with a specific id
    job_sequence = sch.job_sequences.get(id='350020cf-eff6-428a-8484-7078edf532c6:791759af-e8b5-11eb-8015-e592a7dbb2d0')

Retrieving Existing Steps and Jobs of a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can view all existing Steps of a Job Sequence by clicking into that Job Sequence from the Sequences section of the Platform UI as seen below:

.. image:: ../_static/images/run/get_job_sequence_steps.png
|

To retrieve all existing Steps within a Job Sequence using the Platform SDK, you will need to reference the :py:attr:`streamsets.sdk.sch_models.JobSequence.steps` attribute.
You can further filter the available Steps on attributes like ``step_number`` and ``status`` to retrieve specific Step(s):

.. code-block:: python

    # Retrieve all existing Steps
    all_steps = job_sequence.steps

    # Retrieve all Steps with status INACTIVE
    inactive_steps = job_sequence.steps.get_all(status='INACTIVE')

    # Retrieve a Step with a specific step_number
    step = job_sequence.steps.get(step_number='3')

    # Retrieve the Step at step number 3 by indexing
    job_sequence.steps[2]

.. Note::

  Keep in mind that ``step_number`` for all Steps within ``job_sequence.steps`` go from 1->n. However, since they are
  represented in the form of a Python list they will be indexed from 0 -> n-1. That is, index 0 will have
  step_number 1, index 1 will have step_number 2 and so on...

Similarly, you can view the Jobs within a Step of a Job Sequence by referencing the :py:attr:`streamsets.sdk.sch_models.Step.step_jobs` attribute:

.. code-block:: python

    # Retrieve all existing Job instances within the step
    step.step_jobs

    # Returns a list of all Job instances in 'INACTIVE' status
    step.step_jobs.get_all(job_status='INACTIVE')

    # Returns a single Job instance that matches the supplied ID
    step.step_jobs.get(id='acd9dea6-ffcd-4ae0-86e2-bef38c000304:9e1e3faa-ca28-4c05-9edb-3b18aaba4604')

Moving Steps Within a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the UI, once Steps have been added into a Job Sequence, you can move/reorder the Steps by dragging it using the drag icon:

.. image:: ../_static/images/run/move_step.png
|

To move Steps within a Job Sequence using the Platform SDK, pass the :py:class:`streamsets.sdk.sch_models.Step` instance into the :py:meth:`streamsets.sdk.sch_models.JobSequence.move_step` method by specifying the ``target_step_number`` parameter.
This will move the Step from its current location to the step number provided and will reorder the steps that come after the step that was moved.
However, setting the ``swap`` parameter to ``True`` will swap the Step with the Step in the specified ``target_step_number``.

.. code-block:: python

    # Get the Step in step number 3
    step = job_sequence.steps.get(step_number=3)

    # Move the Step to step_number 1. Original order was 1,2,3. Now it is 3,1,2
    job_sequence.move_step(step, 1)

    # Swap the Steps at step_number 3 and step_number 1
    job_sequence.move_step(step, 1, swap=True)

.. Note::
  Calling the :py:meth:`streamsets.sdk.sch_models.JobSequence.move_step` will commit the changes to Platform in addition to updating the in-memory representation of the JobSequence.

Deleting a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~

To delete a Job Sequence in the Platform UI, click the additional options menu near the Job Sequence name and click 'Delete Sequence' on the modal that pops up:

.. image:: ../_static/images/run/delete_job_sequence.png
|

To delete Job Sequences using the Platform SDK, pass in the desired :py:class:`streamsets.sdk.sch_models.JobSequence` instance into the :py:meth:`streamsets.sdk.ControlHub.delete_job_sequences` method:

.. code-block:: python

    # Retrieve the Job Sequence
    job_sequence = sch.job_sequences.get(name='Nightly Job Sequence')

    # Delete the Job Sequence from Platform
    sch.delete_job_sequences(job_sequence)

Updating Metadata of a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Metadata for a Job Sequence includes properties like ``name``, ``description``, ``start_time``, ``end_time``, ``timezone``, and ``crontab_mask``. These properties must be updated separately from the jobs or steps that comprise the content a Job Sequence instance.

To change metadata of a Job Sequence in-memory using the Platform SDK can be done by setting the value of the following attributes: ``name``, ``description``, ``start_time``, ``end_time``, ``timezone`` and ``crontab_mask``.

Once you've updated the relevant properties with new values, pass in the :py:class:`streamsets.sdk.sch_models.JobSequence` instance into the :py:meth:`streamsets.sdk.ControlHub.update_job_sequence_metadata` method:

.. code-block:: python

   # Set the values in local memory
   job_sequence.name = 'Updated Name'
   job_sequence.description = 'Updated Description'
   job_sequence.start_time = '4237401600'
   job_sequence.end_time = 4237996800
   job_sequence.timezone = 'EST'
   job_sequence.crontab_mask = '0/1 * 1/1 * ? *'

   # Update the metadata of the Job Sequence in Platform
   sch.update_job_sequence_metadata(job_sequence)

.. Note::
  Not all properties need to be updated at once in order to propagate the changes to Platform. Properties you don't wish to update can be omitted.


Get the History Log a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To view the History Log of a Job Sequence in the Platform UI, click the additional options menu near a Step and click 'View History' on the modal that pops up:

.. image:: ../_static/images/run/view_history.png
|

To get the history log of a Job Sequence via the Platform SDK, you will need to call the :py:meth:`streamsets.sdk.sch_models.JobSequence.get_history_log` method. This will return a list of :py:class:`streamsets.sdk.sch_models.JobSequenceHistoryLog` instances.
You can filter in the results by passing in values for the ``log_type`` and ``log_level`` parameters:

.. code-block:: python

   # Set the values in local memory
   history_log = job_sequence.get_history_log(log_type='SEQUENCE_CREATE', log_type='INFO')
   history_log

**Output:**

.. code-block:: python

    [<JobSequenceHistoryLog (timestamp=1712006778227, logMessage=Created sequence '60fa6bfa-a72e-465b-98f3-e3c2c81d249b:a2df1e64-dd65-11ed-bee6-3bf718d3c508', logType=SEQUENCE_CREATE, logLevel=INFO)>]

.. Note::
  The acceptable values for ``log_type`` are ``'SEQUENCE_START'``, ``'SCHEDULER_TRIGGER_ERROR'`` & ``'STEP_START'``. On the other hand,
  the acceptable values for ``log_level`` are ``'INFO'``, ``'WARN'`` & ``'ERROR'``.

Mark a Job as Finished Within a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To mark a Job within a Job Sequence as finished, pass in the :py:class:`streamsets.sdk.sch_models.Job` instance into the :py:meth:`streamsets.sdk.sch_models.JobSequence.mark_job_as_finished` method:

.. code-block:: python

   # Mark the Job as finished
   job_sequence.mark_job_as_finished(job)

Run, Enable and Disable a Job Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. Note::
  Running a Job Sequence runs the Jobs within the Sequence in sequential order, enabling a sequence allows it to be run and disabling a sequence stops it from being run.

To run, enable and disable a Job Sequence in the Platform UI, click the additional options menu on the top-right of the Sequence page and follow the pop-up.

.. image:: ../_static/images/run/three_dots_sequence.png
|

If the Sequence is in a 'DISABLED' state, you will be able to run it by clicking on the 'Activate Sequence' button:

.. image:: ../_static/images/run/activate_sequence.png
|

If the Sequence is in a 'ACTIVE' state, you will be able to disable it by clicking on the 'Disable Sequence' button:

.. image:: ../_static/images/run/disable_sequence.png
|

To run a Job Sequence using the Platform SDK, pass in the :py:class:`streamsets.sdk.sch_models.JobSequence` instance into the :py:meth:`streamsets.sdk.ControlHub.run_job_sequence` method:

.. code-block:: python

   # Run the Job Sequence
   sch.run_job_sequence(job_sequence)

Similarly, to enable a Job Sequence pass in the :py:class:`streamsets.sdk.sch_models.JobSequence` instance into the :py:meth:`streamsets.sdk.ControlHub.enable_job_sequence` method:

.. code-block:: python

   # Enable the Job Sequence
   sch.enable_job_sequence(job_sequence)

Similarly, to disable a Job Sequence pass in the :py:class:`streamsets.sdk.sch_models.JobSequence` instance into the :py:meth:`streamsets.sdk.ControlHub.disable_job_sequence` method:

.. code-block:: python

   # Disable the Job Sequence
   sch.disable_job_sequence(job_sequence)

Bringing It All Together
~~~~~~~~~~~~~~~~~~~~~~~~

The complete scripts from this section can be found below.

.. code-block:: python

    # Instantiate the JobSequenceBuilder instance
    job_sequence_builder = sch.get_job_sequence_builder()

    # Add a start condition
    job_sequence_builder.add_start_condition(start_time=4200268800, end_time=4200854400, time_zone='UTC', crontab_mask='0/1 * 1/1 * ? *')

    # Build the Job Sequence instance
    job_sequence = job_sequence_builder.build(name='My Job Sequence', description='My Job Sequence Description')

    # Publish the Job Sequence to Platform
    sch.publish_job_sequence(job_sequence)

    # all_job_sequences = sch.job_sequences
    # nightly_job_sequences = sch.job_sequences.get_all(name='Nightly Job Sequence')
    # job_sequence = sch.job_sequences.get(id='350020cf-eff6-428a-8484-7078edf532c6:791759af-e8b5-11eb-8015-e592a7dbb2d0')
    # all_steps = job_sequence.steps
    # inactive_steps = job_sequence.steps.get_all(status='INACTIVE')
    # step = job_sequence.steps.get(step_number='3')

    # Add three jobs sequentially to the job_sequence
    job_one, job_two, job_three = sch.jobs[0], sch.jobs[1], sch.jobs[2]
    job_sequence.add_step_with_jobs([job_one, job_two, job_three])
    # job_sequence.add_step_with_jobs([job_one, job_two, job_three], parallel_jobs=True)

    # Remove Step from the Job Sequence
    # step = job_sequence.steps[1]
    # job_sequence.remove_step(step)

    # Get the Step in step number 3
    step = job_sequence.steps.get(step_number=3)

    # Move the Step to step_number 1, reordering everything between steps 1-> 3
    job_sequence.move_step(step, 1)
    # job_sequence.move_step(step, 1, swap=True)

    # Add three jobs to the Step
    # step.add_jobs([job_one, job_two, job_three])

    # Remove jobs from the Step
    # step.remove_jobs(job_one, job_two, job_three)

    # Set the values in local memory
    job_sequence.name = 'Updated Name'
    job_sequence.description = 'Updated Description'
    job_sequence.start_time = '4237401600'
    job_sequence.end_time = 4237996800
    job_sequence.timezone = 'EST'
    job_sequence.crontab_mask = '0/1 * 1/1 * ? *'

    # Update the metadata of the Job Sequence in Platform
    sch.update_job_sequence_metadata(job_sequence)

    # Set the values in local memory
    history_log = job_sequence.get_history_log(log_type='SEQUENCE_CREATE', log_type='INFO')

    # Mark the Job as finished
    # job_sequence.mark_job_as_finished(job)

    # Run, Enable & Disable the Job Sequence
    # sch.run_job_sequence(job_sequence)
    # sch.enable_job_sequence(job_sequence)
    # sch.disable_job_sequence(job_sequence)

    # Delete the Job Sequence from SCH
    # sch.delete_job_sequences(job_sequence)
