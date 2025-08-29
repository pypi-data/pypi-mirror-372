GCP Environments
================
|

When using a Google Cloud Platform (GCP) environment, Control Hub connects to your Google Cloud project, provisions the
Google Cloud resources needed to run engines, and deploys engine instances to those resources.

Your GCP administrator must designate a project for the resources, create a Google virtual private cloud (VPC) network,
and configure Google Cloud credentials for Control Hub to use. You then create a GCP environment in Control Hub to
connect to the existing project and VPC network using these credentials.

While the environment is in an active state, Control Hub periodically verifies that the project and VPC network exist
and that the credentials are valid. Control Hub does not provision resources in the VPC network until you create and
start a deployment for this environment.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Environments/GCP.html#concept_pbg_4vl_npb>`_.

Creating Environment with Service Account Impersonation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the UI workflow.
This section shows you how to create a GCP environment with Service Account Impersonation in the UI and how to achieve
the same using StreamSets Platform SDK for Python code step by step.

Define Environment
------------------

In the UI, an environment is defined as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_define_environment.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='GCP')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['gcp-env-tag'],
                                            allow_nightly_builds=False)


Configure GCP Credentials
-------------------------

In the UI, the GCP credentials for an environment are configured as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_configure_credentials_service_account_impersonation.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.credential_type == 'Service Account Impersonation'
    environment.service_account_email = <service account email>
    environment.default_instance_service_account_email = <service account email>   # Optional to set

Configure GCP Project
---------------------

In the UI, the GCP Project for an environment is configured as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_configure_gcp_project.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.project = 'streamsets-engineering'

Configure GCP VPC
-----------------

In the UI, the GCP VPC for an environment is configured as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_select_gcp_vpc.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.vpc_id = 'default'
    environment.gcp_labels = {'name1': 'value1', 'name2': 'value2'}

Review & Activate
-----------------

In the UI, an environment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_review_and_activate.png

|

.. code-block:: python

    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)

Complete example with Service Account Impersonation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

To create a new :py:class:`streamsets.sdk.sch_models.GCPEnvironment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.EnvironmentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_environment_builder` method to instantiate the builder object:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='GCP')

Next, build the  environment by using :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build` method,
and pass the resulting environment object to the :py:meth:`streamsets.sdk.ControlHub.add_environment` method:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='GCP')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['gcp-env-tag'],
                                            allow_nightly_builds=False)
    # Set other configurations for the environment
    environment.credential_type == 'Service Account Impersonation'
    environment.service_account_email = <service account email>
    environment.default_instance_service_account_email = <service account email>   # Optional to set

    environment.project = 'streamsets-engineering'
    environment.vpc_id = 'default'
    environment.gcp_labels = {'name1': 'value1', 'name2': 'value2'}
    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)

Creating Environment with Service Account Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the UI workflow.
This section shows you how to create a GCP environment with Service Account Key in the UI and how to achieve
the same using StreamSets Platform SDK for Python code step by step.

Define Environment
------------------

In the UI, an environment is defined as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_define_environment.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='GCP')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['gcp-env-tag'],
                                            allow_nightly_builds=False)


Configure GCP Credentials
-------------------------

In the UI, the GCP credentials for an environment are configured as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_configure_credentials_service_account_key.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.credential_type == 'Service Account Key'
    environment.account_key_json = <Contents of the Service Account Key as a string>
    environment.default_instance_service_account_email = <service account email>   # Optional to set

Configure GCP Project
---------------------

In the UI, the GCP Project for an environment is configured as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_configure_gcp_project.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.project = 'streamsets-engineering'

Configure GCP VPC
-----------------

In the UI, the GCP VPC for an environment is configured as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_select_gcp_vpc.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.vpc_id = 'default'
    environment.gcp_labels = {'name1': 'value1', 'name2': 'value2'}

Review & Activate
-----------------

In the UI, an environment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/environments/gcp_environments/creation_review_and_activate.png

|

.. code-block:: python

    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)

Complete example with Service Account Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

To create a new :py:class:`streamsets.sdk.sch_models.GCPEnvironment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.EnvironmentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_environment_builder` method to instantiate the builder object:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='GCP')

Next, build the  environment by using :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build` method,
and pass the resulting environment object to the :py:meth:`streamsets.sdk.ControlHub.add_environment` method:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='GCP')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['gcp-env-tag'],
                                            allow_nightly_builds=False)
    # Set other configurations for the environment
    environment.credential_type == 'Service Account Key'
    environment.account_key_json = <Contents of the Service Account Key>
    environment.default_instance_service_account_email = <service account email>   # Optional to set

    environment.project = 'streamsets-engineering'
    environment.vpc_id = 'default'
    environment.gcp_labels = {'name1': 'value1', 'name2': 'value2'}
    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)