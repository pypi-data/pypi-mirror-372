Amazon EC2 Deployments
======================
|
You can create an Amazon EC2 deployment for an active AWS environment.

When you create an Amazon EC2 deployment, you define the engine type, version, and configuration to deploy to the
Amazon VPC specified in the environment. You also specify the number of engine instances to deploy. Each engine
instance runs on a dedicated EC2 instance.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Deployments/AmazonEC2.html#concept_zqg_bnd_z4b>`_.

Creating Deployment for Data Collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
The SDK is designed to mirror the UI workflow.
This section shows you how to create an EC2 deployment for Data Collector in the UI and how to achieve the same using
StreamSets Platform SDK for Python code step by step.

Define the Deployment
---------------------

In the UI, a deployment is defined as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_define_deployment.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='EC2')

    # sample_environment is an instance of streamsets.sdk.sch_models.AWSEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment DC-EXISTING_KEY_PAIR_NAME',
                                          environment=sample_environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['ec2-deployment-tag'])
    sch.add_deployment(deployment)

Configure the Engine
--------------------

In the UI, a deployment's engines are configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_configure_engine.png

|
In the above UI, when you click on `4 stage libraries selected`, the following allows you to select stage libraries.

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_stage_lib_selection_screen.png

|
In the above UI, once you select JDBC and click on any of the '+' signs, it shows the following:

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_stage_lib_selection_as_a_list.png
|
.. include:: stage_libs_sdc.rst

Configure the EC2 Autoscaling Group
-----------------------------------

In the UI, the EC2 Autoscaling Group for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_configure_ec2_autoscaling_group.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.desired_instances = 1
    deployment.ec2_instance_type = 'm4.large'
    # Optional instance_profile, not required if environment has default instance profile set
    deployment.instance_profile = <AWS instance profile>
    deployment.aws_tags = 'owner=stf'

Configure EC2 SSH Access
------------------------

In the UI, the EC2 SSH Access for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_configure_ec2_ssh_access.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.ssh_key_source = 'EXISTING_KEY_PAIR_NAME'
    deployment.key_pair_name = <SSH key pair name>

Review and Launch the Deployment
--------------------------------

In the UI, a deployment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_review_and_launch.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

Complete example for Data Collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
To create a new :py:class:`streamsets.sdk.sch_models.EC2Deployment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method to instantiate the builder object:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='EC2')

Next, retrieve the :py:class:`streamsets.sdk.sch_models.AWSEnvironment` object which represents an active AWS
environment where engine instances will be deployed, pass it to the
:py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method along with other parameters, and pass the
resulting :py:class:`streamsets.sdk.sch_models.EC2Deployment` object to the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    # sample_environment is an instance of streamsets.sdk.sch_models.AWSEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment DC-EXISTING_KEY_PAIR_NAME',
                                          environment=sample_environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['ec2-deployment-tag'])
    sch.add_deployment(deployment)

    deployment.desired_instances = 1
    deployment.ec2_instance_type = 'm4.large'
    # Optional instance_profile, not required if environment has default instance profile set
    deployment.instance_profile = <AWS instance profile>
    deployment.ssh_key_source = 'EXISTING_KEY_PAIR_NAME' # The other valid value is 'NONE'
    deployment.key_pair_name = <SSH key pair name>
    deployment.aws_tags = 'owner=stf'

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['jdbc', 'aws:4.1.0', 'cdp_7_1:4.1.0', 'basic:4.1.0', 'dev']
    # deployment.engine_configuration.stage_libs.append('aws')
    # deployment.engine_configuration.stage_libs.extend(['cassandra_3:4.1.0', 'elasticsearch_7'])

    # Update a deployment's configuration/definition on Control Hub
    sch.update_deployment(deployment)

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)


Creating Deployment for  Transformer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
The SDK is designed to mirror the UI workflow.
This section shows you how to create an EC2 deployment for Transformer in the UI and how to achieve the same using
the StreamSets Platform SDK for Python code step by step.

Define the Deployment
---------------------

In the UI, a deployment is defined as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_transformer_define_deployment.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='EC2')

    # sample_environment is an instance of streamsets.sdk.sch_models.AWSEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment TF-EXISTING_KEY_PAIR_NAME',
                                          environment=sample_environment,
                                          engine_type='TF',
                                          engine_version='4.1.0',
                                          scala_binary_version='2.12',
                                          deployment_tags=['ec2-deployment-tag'])
    sch.add_deployment(deployment)

Configure the Engine
--------------------

In the UI, a deployment's engines are configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_configure_engine.png

In the above UI, when you click on `4 stage libraries selected`, the following allows you to select stage libraries.

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_transformer_stage_lib_selection_screen.png

|
In the above UI, once you select JDBC and click on any of the '+' signs, it shows the following:

.. image:: ../../../_static/images/set_up/deployments/common/creation_configure_engine_transformer_stage_lib_selection_as_a_list.png
|
.. include:: stage_libs_st.rst

Configure the EC2 Autoscaling Group
-----------------------------------

In the UI, the EC2 Autoscaling Group for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_configure_ec2_autoscaling_group.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.desired_instances = 1
    deployment.ec2_instance_type = 'm4.large'
    # Optional instance_profile, not required if environment has default instance profile set
    deployment.instance_profile = <AWS instance profile>
    deployment.aws_tags = 'owner=stf'

Configure EC2 SSH Access
------------------------

In the UI, the EC2 SSH Access for a deployment is configured as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_configure_ec2_ssh_access.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    deployment.ssh_key_source = 'EXISTING_KEY_PAIR_NAME' # The other valid value is 'NONE'
    deployment.key_pair_name = <SSH key pair name>

Review and Launch the Deployment
--------------------------------

In the UI, a deployment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/deployments/ec2_deployments/creation_review_and_launch.png

|
The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

Complete example for Transformer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|
To create a new :py:class:`streamsets.sdk.sch_models.EC2Deployment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.DeploymentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method to instantiate the builder object:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder(deployment_type='EC2')

Next, retrieve the :py:class:`streamsets.sdk.sch_models.AWSEnvironment` object which represents an active AWS
environment where engine instances will be deployed, pass it to the
:py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method along with other parameters, and pass the
resulting :py:class:`streamsets.sdk.sch_models.EC2Deployment` object to the
:py:meth:`streamsets.sdk.ControlHub.add_deployment` method:

.. code-block:: python

    # sample_environment is an instance of streamsets.sdk.sch_models.AWSEnvironment
    deployment = deployment_builder.build(deployment_name='Sample Deployment TF-EXISTING_KEY_PAIR_NAME',
                                          deployment_tags=['ec2-deployment-tag'],
                                          engine_type='TF',
                                          engine_version='4.1.0',
                                          scala_binary_version='2.12',
                                          environment=sample_environment)
    sch.add_deployment(deployment)

    deployment.desired_instances = 1
    deployment.ec2_instance_type = 'm4.large'
    # Optional instance_profile, not required if environment has default instance profile set
    deployment.instance_profile = <AWS instance profile>
    deployment.ssh_key_source = 'EXISTING_KEY_PAIR_NAME' # The other valid value is 'NONE'
    deployment.key_pair_name = <SSH key pair name>
    deployment.aws_tags = 'owner=stf'

    # Optional - add sample stage libs
    deployment.engine_configuration.stage_libs = ['file', 'aws_3_2_0:4.1.0', 'jdbc', 'kafka:4.1.0']
    # deployment.engine_configuration.stage_libs.append('hive:4.1.0')
    # deployment.engine_configuration.stage_libs.extend(['redshift-no-dependency:4.1.0', 'azure_3_2_0'])

    # Update a deployment's configuration/definition on Control Hub
    sch.update_deployment(deployment)

    # Optional - equivalent to clicking on 'Launch Deployment'
    sch.start_deployment(deployment)

