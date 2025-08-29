Self-Managed Deployments
========================
|
You can create a self-managed deployment for an active self-managed environment.
When using a self-managed deployment, you take full control of procuring the resources needed to run engine instances.

When you create a self-managed deployment, you define the engine type, version, and configuration to deploy.
You also select the installation type to use - either a tarball or a Docker image

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Deployments/Self.html#concept_xnm_v5z_gpb>`_.

Using the Data Collector Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
The SDK is designed to mirror the UI workflow. This section shows you how to create a self-managed deployment for
Data Collector using the Docker Image installation type in the UI and how to achieve the same using the StreamSets
Platform SDK for Python code step by step.

Define the Deployment
---------------------

In the UI, a deployment is defined as seen below:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/creation_define_deployment_sdc.png

|
The same effect can be achieved using the :py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class in the SDK. To
instantiate a DeploymentBuilder object, use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder`
method and then provide configuration options to the :py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method
of the builder. Once the deployment object has been built, it can be added to Control Hub using the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='SELF')

    # sample_environment is an instance of streamsets.sdk.sch_models.SelfManagedEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['self-managed-tag'])
    sch.add_deployment(deployment)

Configure the Engine
--------------------

In the UI, a deployment's engines are configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/creation_configure_engine.png

|
When you click on `3 stage libraries selected` in the above UI, the following dialog opens and allows you to select stage libraries:

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_stage_lib_selection_screen.png

|
In the above UI, once you select JDBC and click on any of the '+' signs, then it shows the following:

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_stage_lib_selection_as_a_list.png
|
.. include:: stage_libs_sdc.rst

Configure the Install Type
--------------------------

In the UI, the Install Type for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/select_install_type.png

|
To set the Install Type for the engine in a deployment via the SDK, the ``install_type`` property can be configured
to either ``'TARBALL'`` or ``'DOCKER'`` depending on your needs. If no ``install_type`` is provided, the deployment will
default to ``'TARBALL'``:

.. code-block:: python

    # Set a deployment's install type to use a tarball
    deployment.install_type = 'TARBALL'

    # Or, set a deployment's install type to use the docker image
    deployment.install_type = 'DOCKER'

Review and Launch the Deployment
--------------------------------

In the UI, a deployment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/creation_review_and_launch_sdc.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    # Optional - equivalent to clicking on 'Start & Generate Install Script'
    sch.start_deployment(deployment)

Complete example for the Data Collector Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
To create a new :py:class:`streamsets.sdk.sch_models.SelfManagedDeployment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method to instantiate the builder object:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='SELF')

Next, retrieve the :py:class:`streamsets.sdk.sch_models.SelfManagedEnvironment` object which represents an active
self-managed environment where engine instances will be deployed, pass it to the
:py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method along with other parameters, and pass the
resulting :py:class:`streamsets.sdk.sch_models.SelfManagedDeployment` object to the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:


.. code-block:: python

    # sample_environment is an instance of streamsets.sdk.sch_models.SelfManagedEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['self-managed-tag'])
    sch.add_deployment(deployment)

    deployment.install_type = 'TARBALL'
    # deployment.install_type = 'DOCKER'

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['jdbc', 'aws:4.1.0', 'cdp_7_1:4.1.0', 'basic:4.1.0', 'dev']
    # deployment.engine_configuration.stage_libs.append('aws')
    # deployment.engine_configuration.stage_libs.extend(['cassandra_3:4.1.0', 'elasticsearch_7'])

    # Update a deployment's configuration/definition on Control Hub
    sch.update_deployment(deployment)

    # Optional - equivalent to clicking on 'Start & Generate Install Script'
    sch.start_deployment(deployment)

Using the Transformer Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
The SDK is designed to mirror the UI workflow. This section shows you how to create a self-managed deployment for
Transformer using the Docker Image installation type in the UI and how to achieve the same using StreamSets Platform SDK for Python code step by step.

Define the Deployment
---------------------

In the UI, a deployment is defined as seen below:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/creation_define_deployment_transformer.png

|
The same effect can be achieved using the :py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class in the SDK. To
instantiate a DeploymentBuilder object, use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder`
method and then provide configuration options to the :py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method
of the builder. Once the deployment object has been built, it can be added to Control Hub using the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='SELF')

    # sample_environment is an instance of streamsets.sdk.sch_models.SelfManagedEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='TF',
                                          engine_version='4.1.0',
                                          scala_binary_version='2.11',
                                          deployment_tags=['self-managed-tag'])
    sch.add_deployment(deployment)

Configure the Engine
--------------------

In the UI, a deployment's engines are configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/creation_configure_engine.png

|
When you click on `3 stage libraries selected` in the above UI, the following dialog opens and allows you to select stage libraries:

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_transformer_stage_lib_selection_screen.png

|
In the above UI, once you select JDBC and click on any of the '+' signs, then it shows the following:

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_transformer_stage_lib_selection_as_a_list.png
|
.. include:: stage_libs_st.rst

Configure the Install Type
--------------------------

In the UI, Install Type for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/select_install_type.png

|
To set the Install Type for the engine in a deployment via the SDK, the ``install_type`` property can be configured
to either ``'TARBALL'`` or ``'DOCKER'`` depending on your needs. If no ``install_type`` is provided, the deployment will
default to ``'TARBALL'``:

.. code-block:: python

    # Set a deployment's install type to use the docker image
    deployment.install_type = 'DOCKER'

    # Or, set a deployment's install type to use a tarball
    deployment.install_type = 'TARBALL'

Review and Launch the Deployment
--------------------------------

In the UI, a deployment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/creation_review_and_launch_transformer.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    # Optional - equivalent to clicking on 'Start & Generate Install Script'
    sch.start_deployment(deployment)

Complete example for the Transformer Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
To create a new :py:class:`streamsets.sdk.sch_models.SelfManagedDeployment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method to instantiate the builder object:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='SELF')

Next, retrieve the :py:class:`streamsets.sdk.sch_models.SelfManagedEnvironment` object which represents an active
self-managed environment where engine instances will be deployed, pass it to the
:py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method along with other parameters, and pass the
resulting :py:class:`streamsets.sdk.sch_models.SelfManagedDeployment` object to the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:


.. code-block:: python

    # sample_environment is an instance of streamsets.sdk.sch_models.SelfManagedEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='TF',
                                          engine_version='4.1.0',
                                          scala_binary_version='2.11',
                                          deployment_tags=['self-managed-tag'])
    sch.add_deployment(deployment)

    deployment.install_type = 'DOCKER'
    # deployment.install_type = 'TARBALL'

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['file', 'aws_3_2_0:4.1.0', 'jdbc', 'kafka:4.1.0']
    # deployment.engine_configuration.stage_libs.append('hive:4.1.0')
    # deployment.engine_configuration.stage_libs.extend(['redshift-no-dependency:4.1.0', 'azure_3_2_0'])

    # Update a deployment's configuration/definition on Control Hub
    sch.update_deployment(deployment)

    # Optional - equivalent to clicking on 'Start & Generate Install Script'
    sch.start_deployment(deployment)


Retrieving the Install Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once a self-managed deployment has been successfully created and started, the install script for the deployment's engine(s)
can be retrieved from the deployment's details page in the UI:

.. image:: ../../../_static/images/set_up/deployments/self_managed_deployments/get_install_script.png

|
To retrieve the install script for a deployment via the SDK, use the :py:meth:`streamsets.sdk.sch_models.SelfManagedDeployment.install_script`
method and execute the script according to your requirements:

.. code-block:: python

    install_script = deployment.install_script()

Install scripts have the ability to run in background or foreground.
To retrieve the desired install script pass ``install_mechanism`` to the method :py:meth:`streamsets.sdk.sch_models.SelfManagedDeployment.install_script`.
Available install mechanisms are ``'DEFAULT'``, ``'BACKGORUND'``, ``'FOREGROUND'``.

.. code-block:: python

    install_script = deployment.install_script(install_mechanism='BACKGROUND')

Additionally, install scripts can also be customized to specify which java version can be used.
To set the java version pass ``java_version`` to the method :py:meth:`streamsets.sdk.sch_models.SelfManagedDeployment.install_script`:

.. code-block:: python

    install_script = deployment.install_script(java_version='8')

.. note::
  Supported java versions vary per engine.
  Different engine versions support various java versions.
  Providing an invalid ``java_version`` will result in an error.
  For more information regarding engine java versions, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Deployments/Overview.html#concept_zl3_zlp_q1c>`_.
