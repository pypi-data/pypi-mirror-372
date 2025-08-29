GCE Deployments
===============
|

You can create a Google Compute Engine (GCE) deployment for an active GCP environment.

When you create a GCE deployment, you define the engine type, version, and configuration to deploy to the Google Cloud
project and VPC network specified in the environment. You also specify the number of engine instances to deploy.
Each engine instance runs on a dedicated Google Compute Engine VM instance.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Deployments/GCE.html#concept_grz_g5g_4pb>`_.

Creating Deployment for Data Collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the UI workflow.
This section shows you how to create a GCE deployment for Data Collector in the UI and how to achieve the same using
StreamSets Platform SDK for Python code step by step.

Define the Deployment
---------------------

In the UI, a deployment is defined as seen below:

.. image:: ../../../_static/images/set_up/deployments/gce_deployments/creation_define_deployment_sdc.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='GCE')

    # sample_environment is an instance of streamsets.sdk.sch_models.GCPEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['gce-deployment-tag'])
    sch.add_deployment(deployment)

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

Configure the GCE Region
------------------------

In the UI, the GCE Region for a deployment is selected from a list as seen below:

.. image:: ../../../_static/images/set_up/deployments/gce_deployments/creation_configure_gce_region.png

|

The equivalent configuration in the SDK uses the deployment object's `region` property:

.. code-block:: python

    deployment.region = 'us-west2'

Configure the GCE Zone
----------------------

In the UI, one or more GCE Zones for a deployment are selected from a list as seen below:

.. image:: ../../../_static/images/set_up/deployments/gce_deployments/creation_configure_gce_zone.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.zone = ['us-west2-c']

Configure the GCE Autoscaling Group
-----------------------------------

In the UI, GCE Autoscaling Group for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/gce_deployments/creation_configure_gce_autoscaling_group.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.desired_instances = 1
    deployment.machine_type = 'e2-standard-4'
    deployment.instance_service_account = <Instance Service Account>
    deployment.gcp_labels = {'name1': 'value1', 'name2': 'value2'}
    deployment.network_tags = '<Tag 1>, <Tag 2>'

Configure GCE SSH Access
------------------------

In the UI, GCE SSH Access for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/gce_deployments/creation_configure_gce_ssh_access.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.block_project_ssh_keys = False
    deployment.public_ssh_key = <Public SSH key contents>

Review and Launch the Deployment
--------------------------------

In the UI, a deployment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/deployments/gce_deployments/creation_review_and_launch.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

Complete example for Data Collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

To create a new :py:class:`streamsets.sdk.sch_models.GCEDeployment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method to instantiate the builder object:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='GCE')

Next, retrieve the :py:class:`streamsets.sdk.sch_models.GCPEnvironment` object which represents an active GCP
environment where engine instances will be deployed, pass it to the
:py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method along with other parameters. Finally, pass the
resulting :py:class:`streamsets.sdk.sch_models.GCEDeployment` object to the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    # sample_environment is an instance of streamsets.sdk.sch_models.GCPEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment',
                                          environment=sample_environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['gce-deployment-tag'])
    sch.add_deployment(deployment)

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['jdbc', 'aws:4.1.0', 'cdp_7_1:4.1.0', 'basic:4.1.0', 'dev']
    # deployment.engine_configuration.stage_libs.append('aws')
    # deployment.engine_configuration.stage_libs.extend(['cassandra_3:4.1.0', 'elasticsearch_7'])

    deployment.region = 'us-west2'
    deployment.zone = ['us-west2-c']
    deployment.desired_instances = 1
    deployment.machine_type = 'e2-standard-4'
    deployment.instance_service_account = <Instance Service Account>
    deployment.gcp_labels = {'name1': 'value1', 'name2': 'value2'}
    deployment.network_tags = '<Tag 1>, <Tag 2>'
    deployment.block_project_ssh_keys = False
    deployment.public_ssh_key = <Public SSH key contents>

    # Update a deployment's configuration/definition on Control Hub
    sch.update_deployment(deployment)

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)
