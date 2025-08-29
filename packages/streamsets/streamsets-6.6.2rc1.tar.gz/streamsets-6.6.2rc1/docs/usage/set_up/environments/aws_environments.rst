AWS Environments
================
|

When using an Amazon Web Services (AWS) environment, Control Hub connects to your AWS account,
provisions the AWS resources needed to run engines, and deploys engine instances to those resources.

Your AWS administrator must create an Amazon virtual private cloud (VPC) and configure AWS credentials for Control Hub
to use. You then create an AWS environment in Control Hub to connect to the existing VPC using these credentials.

While the environment is in an active state, Control Hub periodically verifies that the Amazon VPC exists and that the
credentials are valid. Control Hub does not provision resources in the VPC until you create and start a deployment
for this environment.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Environments/AWS.html#concept_q2f_3l1_w4b>`_.

Creating Environment with Cross-Account Role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the UI workflow.
This section shows you how to create an AWS environment with Cross-Account Role in the UI and how to achieve the same
using StreamSets Platform SDK for Python code step by step.

Define Environment
------------------

In the UI, an environment is defined as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_define_environment.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='AWS')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['aws-env-tag'],
                                            allow_nightly_builds=False)

Configure AWS Credentials
-------------------------

In the UI, AWS credentials for an environment are configured as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_configure_engine_configure_cross_account_role.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.credential_type = 'Cross-Account Role'
    environment.role_arn = <role ARN>
    environment.default_instance_profile = <instance profile> # Optional to set

Select AWS Region
-----------------

In the UI, AWS Region for an environment is selected as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_configure_engine_select_aws_region.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.region = 'us-west-2'

Configure AWS VPC
-----------------

In the UI, AWS VPC for an environment is configured as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_configure_engine_configure_aws_vpc.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.vpc_id = 'vpc-08c43530280f249b6'
    environment.aws_tags = {'name1': 'value1', 'name2': 'value2'}

Configure AWS Subnets
---------------------

In the UI, AWS Subnets for an environment are configured as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_configure_engine_configure_aws_subnets.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.subnet_ids = ['subnet-03487f3190fb7db2a']
    environment.security_group_id = 'sg-0ad506cf8e99b14df'

Review & Activate
-----------------

In the UI, an environment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_review_and_activate_environment.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)

Complete example with Cross-Account Role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

To create a new :py:class:`streamsets.sdk.sch_models.AWSEnvironment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.EnvironmentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_environment_builder` method to instantiate the builder object:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='AWS')

Next, build the  environment by using :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build` method,
and pass the resulting environment object to the :py:meth:`streamsets.sdk.ControlHub.add_environment` method:

.. code-block:: python

    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['aws-env-tag'],
                                            allow_nightly_builds=False)
    # Set other configurations for the environment
    environment.credential_type = 'Cross-Account Role'
    environment.role_arn = <role ARN>
    environment.default_instance_profile = <instance profile> # Optional to set
    environment.region = 'us-west-2'
    environment.vpc_id = 'vpc-08c43530280f249b6'
    environment.aws_tags = {'name1': 'value1', 'name2': 'value2'}
    environment.subnet_ids = ['subnet-03487f3190fb7db2a']
    environment.security_group_id = 'sg-0ad506cf8e99b14df'

    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)

Creating Environment with Access Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the UI workflow.
This section shows you how to create an AWS environment with Access Keys in the UI and how to achieve the same
using StreamSets Platform SDK for Python code step by step.

Define Environment
------------------

In the UI, an environment is defined as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_define_environment.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='AWS')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['aws-env-tag'],
                                            allow_nightly_builds=False)

Configure AWS Credentials
-------------------------

In the UI, AWS credentials for an environment are configured as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_configure_engine_configure_access_keys.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.credential_type = 'Access Keys'
    environment.access_key_id = <AWS access key ID>
    environment.secret_access_key = <AWS secret access key>
    environment.default_instance_profile = <instance profile> # Optional to set

Select AWS Region
-----------------

In the UI, AWS Region for an environment is selected as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_configure_engine_select_aws_region.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.region = 'us-west-2'

Configure AWS VPC
-----------------

In the UI, AWS VPC for an environment is configured as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_configure_engine_configure_aws_vpc.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.vpc_id = 'vpc-08c43530280f249b6'
    environment.aws_tags = {'name1': 'value1', 'name2': 'value2'}

Configure AWS Subnets
---------------------

In the UI, AWS Subnets for an environment are configured as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_configure_engine_configure_aws_subnets.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.subnet_ids = ['subnet-03487f3190fb7db2a']
    environment.security_group_id = 'sg-0ad506cf8e99b14df'


Review & Activate
-----------------

In the UI, an environment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/environments/aws_environments/creation_review_and_activate_environment.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)


Complete example with Access Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

To create a new :py:class:`streamsets.sdk.sch_models.AWSEnvironment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.EnvironmentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_environment_builder` method to instantiate the builder object:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='AWS')

Next, build the  environment by using :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build` method,
and pass the resulting environment object to the :py:meth:`streamsets.sdk.ControlHub.add_environment` method:

.. code-block:: python

    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['aws-env-tag'],
                                            allow_nightly_builds=False)
    # Set other configurations for the environment
    environment.credential_type = 'Access Keys'
    environment.access_key_id = <AWS access key ID>
    environment.secret_access_key = <AWS secret access key>
    environment.default_instance_profile = <instance profile> # Optional to set
    environment.region = 'us-west-2'
    environment.vpc_id = 'vpc-08c43530280f249b6'
    environment.aws_tags = {'name1': 'value1', 'name2': 'value2'}
    environment.subnet_ids = ['subnet-03487f3190fb7db2a']
    environment.security_group_id = 'sg-0ad506cf8e99b14df'

    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)
