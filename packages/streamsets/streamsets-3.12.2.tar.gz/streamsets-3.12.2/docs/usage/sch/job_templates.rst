Job Templates
=============
|
Job templates allow you to run multiple job instances with different runtime parameter values from a single template
definition. The SDK allows interaction with job templates including template creation, starting a job from a template,
spawning multiple job instances from a template, and template deletion.

Creating a Job Template
~~~~~~~~~~~~~~~~~~~~~~~

To create a new job template and add it to Control Hub, use the :py:class:`streamsets.sdk.sch_models.JobBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_job_builder` method to instantiate the builder object.

Simply pass ``job_template=True`` to the :py:meth:`streamsets.sdk.sch_models.JobBuilder.build` method, and then pass the
resulting job object to the :py:meth:`streamsets.sdk.ControlHub.add_job` method:

.. code-block:: python

    job_builder = sch.get_job_builder()
    job_template = job_builder.build('Job Template using SDK',
                                     pipeline=simple_pipeline,
                                     job_template=True,
                                     runtime_parameters={'x': 'y', 'a': 'b'})
    sch.add_job(job_template)

Starting Job Instances using Job Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting a job from a job template is very similar to starting any other job - with a few additional
requirements. Due to the nature of a job template, it expects that various values will be supplied for the
``runtime_parameters`` at start time, and likewise expects an ``instance_name_suffix`` to be provided at start time.

The ``runtime_parameters`` is optional and will default to the job template's default set of parameters if none are
supplied at start time.

The ``instance_name_suffix`` is appended to the end of the job template name to uniquely identify each job instance
started from the template. Additional details on the suffix can be found in the `Control Hub documentation <https://docs.streamsets.com/portal/#controlhub/latest/help/controlhub/UserGuide/Jobs/JobTemplates.html#concept_wmc_h2c_4fb>`_,
and in the API reference for the :py:meth:`streamsets.sdk.ControlHub.start_job_template` method.

To start a job instance from a template, use the :py:meth:`streamsets.sdk.ControlHub.start_job_template`
method and pass in the ``runtime_parameters`` and ``instance_name_suffix`` values:

.. code-block:: python

    # Get the job template to start the job from
    job_template = sch.jobs.get(name='Job Template using SDK')

    # Generate some runtime parameters to be used in the job
    runtime_parameters = [{'x': '1', 'a': 'b'}, {'x': '2', 'a': 'b'}]

    # Pass in the runtime parameters, specify the suffix type as 'PARAM_VALUE' and the corresponding parameter_name
    # as 'x', i.e. the value 'x' will be appended to the end of this job's name upon startup
    jobs = sch.start_job_template(simple_job_template,
                                  instance_name_suffix='PARAM_VALUE',
                                  parameter_name='x',
                                  runtime_parameters=runtime_parameters)

Spawning multiple Job instances using same parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK also allows you to spawn multiple job instances from the same template, all using the same runtime parameters.
Simply include a value for ``number_of_instances`` in the :py:meth:`streamsets.sdk.ControlHub.start_job_template` method
to specify the number of Job instances to be spawned using the specified runtime parameters:

.. code-block:: python

    job_template = sch.jobs.get(name='Job Template using SDK')
    jobs = sch.start_job_template(simple_job_template, number_of_instances=3)

In this case, since ``runtime_parameters`` is not specified, the default set of parameters specified when creating the
Job Template are used.

Deleting a Job Template
~~~~~~~~~~~~~~~~~~~~~~~

Deleting a job template is identical to the steps required to delete a job from Control Hub. Simply retrieve the
:py:class:`streamsets.sdk.sch_models.Job` instance you wish to delete, and pass it to the :py:meth:`streamsets.sdk.ControlHub.delete_job`
method:

.. code-block:: python

    sch.delete_job(job_template)

