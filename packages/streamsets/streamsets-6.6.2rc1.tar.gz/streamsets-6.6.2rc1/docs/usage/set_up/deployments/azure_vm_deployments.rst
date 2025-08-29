Azure VM Deployments
====================
|

You can create an Azure Virtual Machine (Azure VM) deployment for an active Azure environment.

When you create an Azure VM deployment, you define the engine type, version, and configuration to deploy to the Azure
virtual network (VNet) specified in the environment. You also specify the number of engine instances to deploy. Each
engine instance runs on a dedicated VM instance.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Deployments/AzureVM.html#concept_gc5_hpr_gqb>`_.

Creating a Deployment for Data Collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the UI workflow.
This section shows you how to create an Azure VM deployment for Data Collector in the UI and how to achieve the same
using StreamSets Platform SDK for Python code step by step.

Define the Deployment
---------------------

In the UI, a deployment is defined as seen below:

.. image:: ../../../_static/images/set_up/deployments/azure_vm_deployments/creation_define_deployment_sdc.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='AZURE_VM')

    # sample_environment is an instance of streamsets.sdk.sch_models.AzureEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='DC',
                                          engine_version='4.2.0',
                                          deployment_tags=['azure-dep-tag'])

Configure the Engine
--------------------

In the UI, a deployment's engines are configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/gce_deployments/creation_configure_engine.png

|

In the above UI, when you click on 3 stage libraries selected, the following dialog opens and allows you to select
stage libraries.

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_stage_lib_selection_screen.png

|

In the above UI, once you select JDBC and click on any of the '+' signs, then it shows the following:

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_stage_lib_selection_as_a_list.png

|
.. include:: stage_libs_sdc.rst

You can also configure an external resource as well as engine labels for the deployment:

.. code-block:: python

    # Optional - set external resource source and engine labels
    deployment.engine_configuration.external_resource_source = <External resource source>
    deployment.engine_configuration.engine_labels = ['sampledeployment']

Configure the Azure VM Autoscaling Group
----------------------------------------

In the UI, the Azure VM Autoscaling Group for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/azure_vm_deployments/creation_configure_azure_vm_autoscaling_group.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.desired_instances = 1
    deployment.vm_size = 'Standard_D4s_v2'
    deployment.managed_identity = 'csp-identity'
    deployment.resource_group = 'azure-csp'
    deployment.azure_tags = {'name1': 'value1', 'name2': 'value2'}

Configure Azure VM SSH Access
-----------------------------

In the UI, the Azure VM SSH Access for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/azure_vm_deployments/creation_configure_azure_vm_ssh_access.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.ssh_key_source = 'Existing SSH Key Pair Name'
    deployment.key_pair_name = <SSH key pair name>
    deployment.attach_public_ip = False

Review and Launch the Deployment
--------------------------------

In the UI, a deployment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/deployments/azure_vm_deployments/creation_review_and_launch.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    sch.add_deployment(deployment)
    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

Complete example for Data Collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

To create a new :py:class:`streamsets.sdk.sch_models.AzureVMDeployment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method to instantiate the builder object:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='AZURE_VM')

Next, retrieve the :py:class:`streamsets.sdk.sch_models.AzureEnvironment` object which represents an active Azure
environment where engine instances will be deployed, pass it to the
:py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method along with other parameters. Finally, pass the
resulting :py:class:`streamsets.sdk.sch_models.AzureVMDeployment` object to the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    # sample_environment is an instance of streamsets.sdk.sch_models.AzureEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='DC',
                                          engine_version='4.2.0',
                                          deployment_tags=['azure-dep-tag'])

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['jdbc', 'aws:4.1.0', 'cdp_7_1:4.3.0', 'basic:4.3.0', 'dev']
    # deployment.engine_configuration.stage_libs.append('aws')
    # deployment.engine_configuration.stage_libs.extend(['cassandra_3:4.3.0', 'elasticsearch_7'])

    # Optional - set external resource source and engine labels
    deployment.engine_configuration.external_resource_source = <External resource source>
    deployment.engine_configuration.engine_labels = ['sampledeployment']

    deployment.desired_instances = 1
    deployment.vm_size = 'Standard_D4s_v2'
    deployment.managed_identity = 'csp-identity'
    deployment.resource_group = 'azure-csp'
    deployment.azure_tags = {'name1': 'value1', 'name2': 'value2'}

    deployment.ssh_key_source = 'Existing SSH Key Pair Name'
    deployment.key_pair_name = <SSH key pair name>
    deployment.attach_public_ip = False

    sch.add_deployment(deployment)
    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)


Creating a Deployment for Transformer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the UI workflow.
This section shows you how to create an Azure VM deployment for Transformer in the UI and how to achieve the same
using StreamSets Platform SDK for Python code step by step.

Define the Deployment
---------------------

In the UI, a deployment is defined as seen below:

.. image:: ../../../_static/images/set_up/deployments/azure_vm_deployments/creation_define_deployment_transformer.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='AZURE_VM')

    # sample_environment is an instance of streamsets.sdk.sch_models.AzureEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='TF',
                                          engine_version='4.1.0',
                                          scala_binary_version='2.11.0',
                                          deployment_tags=['azure-dep-tag'])

Configure the Engine
--------------------

In the UI, a deployment's engines are configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/gce_deployments/creation_configure_engine.png

|

In the above UI, when you click on 3 stage libraries selected, the following dialog opens and allows you to select
stage libraries.

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_transformer_stage_lib_selection_screen.png

|

In the above UI, once you select JDBC and click on any of the '+' signs, then it shows the following:

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_transformer_stage_lib_selection_as_a_list.png

|
.. include:: stage_libs_st.rst

You can also configure an external resource as well as engine labels for the deployment:

.. code-block:: python

    # Optional - set external resource source and engine labels
    deployment.engine_configuration.external_resource_source = <External resource source>
    deployment.engine_configuration.engine_labels = ['sampledeployment']

Configure the Azure VM Autoscaling Group
----------------------------------------

In the UI, the Azure VM Autoscaling Group for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/azure_vm_deployments/creation_configure_azure_vm_autoscaling_group.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.desired_instances = 1
    deployment.vm_size = 'Standard_D4s_v2'
    deployment.managed_identity = 'csp-identity'
    deployment.resource_group = 'azure-csp'
    deployment.azure_tags = {'name1': 'value1', 'name2': 'value2'}

Configure Azure VM SSH Access
-----------------------------

In the UI, the Azure VM SSH Access for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/azure_vm_deployments/creation_configure_azure_vm_ssh_access.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.ssh_key_source = 'Existing SSH Key Pair Name'
    deployment.key_pair_name = <SSH key pair name>
    deployment.attach_public_ip = False

Review and Launch the Deployment
--------------------------------

In the UI, a deployment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/deployments/azure_vm_deployments/creation_review_and_launch.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    sch.add_deployment(deployment)
    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)


Complete example for Transformer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

To create a new :py:class:`streamsets.sdk.sch_models.AzureVMDeployment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method to instantiate the builder object:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='AZURE_VM')

Next, retrieve the :py:class:`streamsets.sdk.sch_models.AzureEnvironment` object which represents an active Azure
environment where engine instances will be deployed, pass it to the
:py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method along with other parameters. Finally, pass the
resulting :py:class:`streamsets.sdk.sch_models.AzureVMDeployment` object to the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    # sample_environment is an instance of streamsets.sdk.sch_models.AzureEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='TF',
                                          engine_version='4.1.0',
                                          scala_binary_version='2.11.0',
                                          deployment_tags=['azure-dep-tag'])

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['file', 'aws_3_2_0:4.2.0', 'jdbc', 'kafka:4.2.0']
    # deployment.engine_configuration.stage_libs.append('hive:4.2.0')
    # deployment.engine_configuration.stage_libs.extend(['redshift-no-dependency:4.2.0', 'azure_3_2_0'])

    # Optional - set external resource source
    deployment.engine_configuration.external_resource_source = <External resource source>
    deployment.engine_configuration.engine_labels = ['sampledeployment']

    deployment.desired_instances = 1
    deployment.vm_size = 'Standard_D4s_v2'
    deployment.managed_identity = 'csp-identity'
    deployment.resource_group = 'azure-csp'
    deployment.azure_tags = {'name1': 'value1', 'name2': 'value2'}
    deployment.ssh_key_source = 'Existing SSH Key Pair Name'
    deployment.key_pair_name = <SSH key pair name>
    deployment.attach_public_ip = False

    sch.add_deployment(deployment)
    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

