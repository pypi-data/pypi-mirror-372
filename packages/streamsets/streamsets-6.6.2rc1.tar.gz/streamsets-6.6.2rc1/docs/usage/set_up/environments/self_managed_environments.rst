Self-Managed Environments
=========================
|
When using a self-managed environment, you take full control of procuring the resources needed to run and deploy engine
instances. A self-managed environment can represent local on-premises machines or cloud computing instances.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Environments/Self.html#concept_tfz_lrz_gpb>`_.

Creating a Self-Managed Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
The SDK is designed to mirror the UI workflow.
This section shows you how to create a Self-Manged environment in the UI and how to achieve the same using StreamSets
Platform SDK for Python code step by step.

Define Environment
------------------
In the UI, an environment is defined as seen below:

.. image:: ../../../_static/images/set_up/environments/self_managed_environments/creation_define_environment.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='SELF')

    environment = environment_builder.build(environment_name='Self-managed-environment',
                                            environment_tags=['self-managed-tag'],
                                            allow_nightly_engine_builds=False)
Review and Launch
-----------------
In the UI, an environment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/environments/self_managed_environments/creation_review_and_activate.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)

Complete example for Self-Managed Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
To create a new :py:class:`streamsets.sdk.sch_models.SelfManagedEnvironment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.EnvironmentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_environment_builder` method to instantiate the builder object:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='SELF')

|
Next, build the  environment by using :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build` method,
and pass the resulting environment object to the :py:meth:`streamsets.sdk.ControlHub.add_environment` method:

.. code-block:: python

    environment = environment_builder.build(environment_name='Self-managed-environment',
                                            environment_tags=['self-managed-tag'],
                                            allow_nightly_engine_builds=False)
    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)
