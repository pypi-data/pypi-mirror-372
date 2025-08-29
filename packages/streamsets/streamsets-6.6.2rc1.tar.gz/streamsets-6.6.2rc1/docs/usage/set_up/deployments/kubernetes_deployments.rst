.. _Kubernetes Deployments:

Kubernetes Deployments
======================

You can create a Kubernetes deployment for an active Kubernetes environment.

If you have not yet created a Kubernetes environment or are unsure of the prerequisite requirements, please refer to the SDK documentation section on :ref:`Kubernetes Environments`.

When you create a Kubernetes deployment, you define the type of engine, the engine version, and Kubernetes configuration to use to deploy to the Kubernetes cluster specified in the environment you provide.
You can also specify the desired number of engine instances, enable autoscaling, and set specific Kubernetes deployment configurations.

For more information on Kubernetes deployments, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Deployments/Kubernetes.html#concept_ec3_cqg_hvb>`_.

Creating a Deployment for Data Collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK is designed to mirror the workflow seen in the Platform UI.
This section shows you how to create a Kubernetes Data Collector deployment in the UI, and the step-by-step equivalent using the StreamSets Platform SDK for Python.

Define the Deployment
---------------------

In the Platform UI, a Kubernetes deployment can be defined using the wizard as seen below:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/sdc_create_deployment_wizard.png

|

The equivalent steps to define and create a deployment using the SDK require that you have the :py:class:`streamsets.sdk.sch_models.KubernetesEnvironment` instance handy.
To create a deployment for your environment, start by retrieving an instance of :py:class:`streamsets.sdk.sch_models.DeploymentBuilder`.
This is done via the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method, specifying the ``deployment_type`` as ``'KUBERNETES'``.
Once the :py:class:`streamsets.sdk.sch_models.DeploymentBuilder` instance has been retrieved, a deployment can be created using the :py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method.
You'll need to specify key details for the deployment like ``deployment_name``, ``engine_type``, ``engine_version``, and ``deployment_tags``.

Finally, pass the newly-built :py:class:`streamsets.sdk.sch_models.KubernetesDeployment` object to the :py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    environment = sch.environments.get(environment_id='<environment_id>')        # Retrieve an environment by id
    # environment = sch.environments.get(environment_name='<environment_name>')    Alternatively, retrieve an environment by name

    deployment_builder = sch.get_deployment_builder(deployment_type='KUBERNETES')
    deployment = deployment_builder.build(deployment_name='Sample Kubernetes Deployment',
                                          environment=environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['k8s-sdc-4.1.0'])
    sch.add_deployment(deployment)

Configure the Engine
--------------------

In the Platform UI, a Kubernetes deployment's engine(s) can be configured using the wizard as seen below:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/sdc_configure_deployment_wizard.png

|

Clicking on the `3 stage libraries selected` option allows you to select which stage libraries to install on the engines for the deployment.
You can select categories for the stage libraries or search for individual stage libraries by name as seen in the example below:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/sdc_stage_libs_wizard.png

|

Selecting the ``+`` symbol to add a stage library allows you to select the version of the stage library you wish to add to the deployment.
For example, if you were to add the ``JDBC Lookup`` stage to your deployment, you would see a selection similar to the following:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/sdc_jdbc_version_wizard.png
|
.. include:: stage_libs_sdc.rst

Configure the Kubernetes Deployment
-----------------------------------

In the Platform UI, you can also set Kubernetes-specific configurations for the deployment including options like the desired number of instances, CPU and Memory limits, or Kubernetes labels:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/sdc_configure_kubernetes_wizard.png

|

The same configuration can be set via the SDK by simply referencing the configuration properties of the :py:class:`streamsets.sdk.sch_models.KubernetesDeployment` you generated in the previous step:

.. code-block:: python

    # Set Kubernetes configurations for the deployment
    deployment.kubernetes_labels = {'environment': 'streamsets'}
    deployment.desired_instances = 2
    deployment.cpu_request = '1.0'
    deployment.memory_request = '1Gi'
    deployment.memory_limit = '4Gi'

Review and Launch the Deployment
--------------------------------

In the Platform UI, you can review and launch your Kubernetes deployment as seen below:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/sdc_review_launch_wizard.png

|

To launch your Kubernetes deployment using the SDK, use the :py:meth:`streamsets.sdk.ControlHub.start_deployment` method and pass in the :py:class:`streamsets.sdk.sch_models.KubernetesDeployment` instance you wish to start:

.. code-block:: python

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

Bringing It All Together
------------------------

The complete scripts from this section can be found below. Commands that only served to verify some output from the
example have been removed.

.. code-block:: python

    environment = sch.environments.get(environment_id='<environment_id>')        # Retrieve an environment by id
    # environment = sch.environments.get(environment_name='<environment_name>')    Alternatively, retrieve an environment by name

    deployment_builder = sch.get_deployment_builder(deployment_type='KUBERNETES')
    deployment = deployment_builder.build(deployment_name='Sample Kubernetes Deployment',
                                          environment=environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['k8s-sdc-4.1.0'])
    sch.add_deployment(deployment)

    # Set Kubernetes configurations for the deployment
    deployment.kubernetes_labels = {'environment': 'streamsets'}
    deployment.desired_instances = 2
    deployment.cpu_request = '1.0'
    deployment.memory_request = '1Gi'
    deployment.memory_limit = '4Gi'

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['jdbc', 'aws:4.1.0', 'cdp_7_1:4.1.0', 'basic:4.1.0', 'dev']
    # deployment.engine_configuration.stage_libs.append('aws')
    # deployment.engine_configuration.stage_libs.extend(['cassandra_3:4.1.0', 'elasticsearch_7'])

    # Update the deployment's configuration/definition on Control Hub
    sch.update_deployment(deployment)

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

Creating a Deployment for Transformer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK is designed to mirror the workflow seen in the Platform UI.
This section shows you how to create a Kubernetes Transformer deployment in the UI, and the step-by-step equivalent using the StreamSets Platform SDK for Python.

Define the Deployment
---------------------

In the Platform UI, a Kubernetes deployment can be defined using the wizard as seen below:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/transformer_create_deployment_wizard.png

|

The equivalent steps to define and create a deployment using the SDK require that you have the :py:class:`streamsets.sdk.sch_models.KubernetesEnvironment` instance handy.
To create a deployment for your environment, start by retrieving an instance of :py:class:`streamsets.sdk.sch_models.DeploymentBuilder`.
This is done via the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method, specifying the ``deployment_type`` as ``'KUBERNETES'``.
Once the :py:class:`streamsets.sdk.sch_models.DeploymentBuilder` instance has been retrieved, a deployment can be created using the :py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method.
You'll need to specify key details for the deployment like ``deployment_name``, ``engine_type``, ``engine_version``, ``scala_binary_version``, and ``deployment_tags``.

Finally, pass the newly-built :py:class:`streamsets.sdk.sch_models.KubernetesDeployment` object to the :py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    environment = sch.environments.get(environment_id='<environment_id>')        # Retrieve an environment by id
    # environment = sch.environments.get(environment_name='<environment_name>')    Alternatively, retrieve an environment by name

    deployment_builder = sch.get_deployment_builder(deployment_type='KUBERNETES')
    deployment = deployment_builder.build(deployment_name='Sample Kubernetes Deployment',
                                          environment=environment,
                                          engine_type='TF',
                                          engine_version='4.1.0',
                                          scala_binary_version='2.12',
                                          deployment_tags=['k8s-transformer-4.1.0'])
    sch.add_deployment(deployment)

Configure the Engine
--------------------

In the Platform UI, a Kubernetes deployment's engine(s) can be configured using the wizard as seen below:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/transformer_configure_deployment_wizard.png

|

Clicking on the `2 stage libraries selected` option allows you to select which stage libraries to install on the engines for the deployment.
You can select categories for the stage libraries or search for individual stage libraries by name as seen in the example below:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/transformer_stage_libs_wizard.png

|

Selecting the ``+`` symbol to add a stage library allows you to select the version of the stage library you wish to add to the deployment.
For example, if you were to add the ``JDBC Lookup`` stage to your deployment, you would see a selection similar to the following:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/transformer_jdbc_version_wizard.png
|
.. include:: stage_libs_st.rst

Configure the Kubernetes Deployment
-----------------------------------

In the Platform UI, you can also set Kubernetes-specific configurations for the deployment including options like the desired number of instances, CPU and Memory limits, or Kubernetes labels:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/sdc_configure_kubernetes_wizard.png

|

The same configuration can be set via the SDK by simply referencing the configuration properties of the :py:class:`streamsets.sdk.sch_models.KubernetesDeployment` you generated in the previous step:

.. code-block:: python

    # Set Kubernetes configurations for the deployment
    deployment.kubernetes_labels = {'environment': 'streamsets'}
    deployment.desired_instances = 2
    deployment.cpu_request = '1.0'
    deployment.memory_request = '1Gi'
    deployment.memory_limit = '4Gi'

Review and Launch the Deployment
--------------------------------

In the Platform UI, you can review and launch your Kubernetes deployment as seen below:

.. image:: ../../../_static/images/set_up/deployments/kubernetes_deployments/sdc_review_launch_wizard.png

|

To launch your Kubernetes deployment using the SDK, use the :py:meth:`streamsets.sdk.ControlHub.start_deployment` method and pass in the :py:class:`streamsets.sdk.sch_models.KubernetesDeployment` instance you wish to start:

.. code-block:: python

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

Bringing It All Together
------------------------

The complete scripts from this section can be found below. Commands that only served to verify some output from the
example have been removed.

.. code-block:: python

    environment = sch.environments.get(environment_id='<environment_id>')        # Retrieve an environment by id
    # environment = sch.environments.get(environment_name='<environment_name>')    Alternatively, retrieve an environment by name

    deployment_builder = sch.get_deployment_builder(deployment_type='KUBERNETES')
    deployment = deployment_builder.build(deployment_name='Sample Kubernetes Deployment',
                                          environment=environment,
                                          engine_type='TF',
                                          engine_version='4.1.0',
                                          scala_binary_version='2.12',
                                          deployment_tags=['k8s-sdc-4.1.0'])
    sch.add_deployment(deployment)

    # Set Kubernetes configurations for the deployment
    deployment.kubernetes_labels = {'environment': 'streamsets'}
    deployment.desired_instances = 2
    deployment.cpu_request = '1.0'
    deployment.memory_request = '1Gi'
    deployment.memory_limit = '4Gi'

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['file', 'aws_3_2_0:4.1.0', 'jdbc', 'kafka:4.1.0']
    # deployment.engine_configuration.stage_libs.append('hive:4.1.0')
    # deployment.engine_configuration.stage_libs.extend(['redshift-no-dependency:4.1.0', 'azure_3_2_0'])

    # Update the deployment's configuration/definition on Control Hub
    sch.update_deployment(deployment)

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)
