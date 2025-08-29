Managing Environments
=====================
|
When you manage environments, you can filter the list of displayed environments, activate or deactivate environments,
and edit environments.
When needed, you can delete an environment when no deployments belong to it.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Environments/Managing.html#concept_w2y_45h_dqb>`_.

In the UI, an environment is managed as seen below:

.. image:: ../../../_static/images/set_up/environments/managing_environments/managing_environments.png

|

Retrieving Environments
~~~~~~~~~~~~~~~~~~~~~~~
|
To retrieve existing environments from a Control Hub instance, you can reference the
:py:attr:`streamsets.sdk.ControlHub.environments` attribute of your :py:class:`streamsets.sdk.ControlHub` instance:

.. code-block:: python

    sch.environments

**Output:**

.. code-block:: python

    [<SelfManagedEnvironment (environment_id=b196e4ee-e655-470d-9e6e-59f19ab46bed:3bb73836-b7ec-11eb-b93c-758d73010046,
      environment_name=Sample Environment, environment_type=SELF, state=ACTIVE)>,
     <SelfManagedEnvironment (environment_id=6f2863ad-030d-48a3-a6bc-6162b757511a:3bb73836-b7ec-11eb-b93c-758d73010046,
      environment_name=Sample Environment 2, environment_type=SELF, state=ACTIVE)>]

Filtering Environments
~~~~~~~~~~~~~~~~~~~~~~
|
You can also further filter and refine the environments based on attributes like ``environment_name`` or
``environment_id``:

.. code-block:: python

    sch.environments.get(environment_name='Sample Environment')

**Output:**

.. code-block:: python

    <SelfManagedEnvironment (environment_id=b196e4ee-e655-470d-9e6e-59f19ab46bed:3bb73836-b7ec-11eb-b93c-758d73010046,
     environment_name=Sample Environment, environment_type=SELF, state=ACTIVE)>

.. code-block:: python

    sch.environments.get(environment_id='b196e4ee-e655-470d-9e6e-59f19ab46bed:3bb73836-b7ec-11eb-b93c-758d73010046')

**Output:**

.. code-block:: python

    <SelfManagedEnvironment (environment_id=b196e4ee-e655-470d-9e6e-59f19ab46bed:3bb73836-b7ec-11eb-b93c-758d73010046,
     environment_name=Sample Environment, environment_type=SELF, state=ACTIVE)>

Activating Environments
~~~~~~~~~~~~~~~~~~~~~~~
|
You must activate an environment before you can create deployments for the environment. You can activate an environment
when you create it, or you can activate it at a later time.
You can activate an environment that is in the Deactivated or Deactivation Error state.
To activate an environment, pass one or more instances of :py:class:`streamsets.sdk.sch_models.Environment` to
the :py:meth:`streamsets.sdk.ControlHub.activate_environment` method:

.. code-block:: python

    sample_environment = sch.environments.get(environment_name='Sample Environment')
    sch.activate_environment(sample_environment)
    assert sample_environment.state == 'ACTIVE'

Deactivating Environments
~~~~~~~~~~~~~~~~~~~~~~~~~
|
Deactivate an environment when you want to temporarily prevent engine instances from being deployed to it, thereby
preventing new deployments from being created.
You can deactivate an environment that meets the following conditions:

* The environment is in the Active or Activation Error state.

* No active deployments belong to the environment.

To deactivate an environment, pass one or more instances of :py:class:`streamsets.sdk.sch_models.Environment` to
the :py:meth:`streamsets.sdk.ControlHub.deactivate_environment` method:

.. code-block:: python

    sample_environment = sch.environments.get(environment_name='sample environment')
    sch.deactivate_environment(sample_environment)
    assert sample_environment.state == 'DEACTIVATED'

Editing Environments
~~~~~~~~~~~~~~~~~~~~
|
You can edit environments when they are in any state except for the transient Activating and Deactivating states.
When you edit an active environment, active deployments might be impacted due to deployments inheriting values from the
parent environment.
To update an environment, pass the updated :py:class:`streamsets.sdk.sch_models.Environment` instance to
the :py:meth:`streamsets.sdk.ControlHub.update_environment` method:

.. code-block:: python

    sample_environment = sch.environments.get(environment_name='sample environment')
    sample_environment.environment_name = 'updated name'
    sample_environment.tags = sample_environment.tags + ['updatedTag']
    sch.update_environment(sample_environment)

Deleting Environments
~~~~~~~~~~~~~~~~~~~~~
|
Delete an environment when you no longer want to deploy engine instances to it.
You can delete an environment that meets the following conditions:

* The environment is in the Setup Incomplete, Deactivated, or Deactivation Error state.

* No deployments belong to the environment.

To delete an environment, pass one or more instances of :py:class:`streamsets.sdk.sch_models.Environment` to
the :py:meth:`streamsets.sdk.ControlHub.delete_environment` method:

.. code-block:: python

    sample_environment = sch.environments.get(environment_name='sample environment')
    sch.delete_environment(sample_environment)

