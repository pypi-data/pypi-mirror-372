Self-Managed Deployment samples
===============================
|

The following section includes example scripts of some common tasks and objectives for Self-Managed Deployments.

These examples are intended solely as a jumping-off point for developers new to the SDK; to provide an idea of how
some common tasks might be written out programmatically using the tools and resources available in the SDK.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Deployments/Self.html#concept_xnm_v5z_gpb>`_.

To help visualize the environment and deployment that this example builds, here is the representation of the environment
and deployment as it appears in the StreamSets Platform UI:

**Environment**

.. image:: ../../_static/sdk_sample_self_managed_environment.png
|

**Deployment**

.. image:: ../../_static/sdk_sample_self_managed_deployment.png
|

**Deployment Details**

.. image:: ../../_static/sdk_sample_self_managed_deployment_details.png
|

Create a Self-Managed Deployment
--------------------------------
|
This example will show how to use the SDK to create and start a brand new Self-Managed Deployment on the StreamSets
Platform.

.. _script-example2:

.. code-block:: python

    # Import the ControlHub class from the SDK.
    from streamsets.sdk import ControlHub

    # Connect to the StreamSets Platform.
    sch = ControlHub(credential_id=<credential id>, token=<token>)

    # Instantiate an EnvironmentBuilder instance to build an environment, and activate it.
    environment_builder = sch.get_environment_builder(environment_type='SELF')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_type='SELF',
                                            environment_tags=['self-managed-tag'],
                                            allow_nightly_engine_builds=False)
    # Add the environment and activate it
    sch.add_environment(environment)
    sch.activate_environment(environment)

    # Instantiate the DeploymentBuilder instance to build the deployment
    deployment_builder = sch.get_deployment_builder(deployment_type='SELF')

    # Build the deployment and specify the Sample Environment created previously.
    deployment = deployment_builder.build(deployment_name='Sample Deployment DC-DOCKER',
                                          deployment_type='SELF',
                                          environment=environment,
                                          engine_type='DC',
                                          engine_version='4.1.0',
                                          deployment_tags=['self-managed-tag'])
    deployment.install_type = 'DOCKER'

    # Add the deployment to SteamSets Platform, and start it
    sch.add_deployment(deployment)
    sch.start_deployment(deployment)

Fetch Self-Managed Deployments
------------------------------
|
This example will show how to use the SDK to fetch Self-Managed Deployments.

.. _script-example3:

.. code-block:: python

    # Import the ControlHub class from the SDK.
    from streamsets.sdk import ControlHub

    # Connect to the StreamSets Platform.
    sch = ControlHub(credential_id=<credential id>, token=<token>)

    # Fetch by deployment_name
    fetched_by_name_deployment = sch.deployments.get(deployment_name='Sample Deployment DC-DOCKER')

    # Fetch by id
    deployment_id = fetched_by_name_deployment.deployment_id
    fetched_by_id_deployment = sch.deployments.get(deployment_id=deployment_id)

    # Fetch all the deployments
    all_deployments = sch.deployments


Start/Stop Self-Managed Deployments
-----------------------------------
|
This example will show how to use the SDK to start and stop Self-Managed Deployments.

.. _script-example4:

.. code-block:: python

    # Import the ControlHub class from the SDK.
    from streamsets.sdk import ControlHub

    # Connect to the StreamSets Platform.
    sch = ControlHub(credential_id=<credential id>, token=<token>)

    sample_deployment = sch.deployments.get(deployment_name='Sample Deployment DC-DOCKER')

    # Start
    sch.start_deployment(sample_deployment)
    assert sample_deployment.state == 'ACTIVE'

    # Stop
    sch.stop_deployment(sample_deployment)
    assert deployment.state == 'DEACTIVATED'

Update Self-Managed Deployment
------------------------------
|
This example will show how to use the SDK to update a Self-Managed Deployment. This includes how to update stage
libraries, external resources, and a few other configurations of the deployment.


.. _script-example5:

.. code-block:: python

    # Import the ControlHub class from the SDK.
    from streamsets.sdk import ControlHub

    # Connect to the StreamSets Platform.
    sch = ControlHub(credential_id=<credential id>, token=<token>)
    # Fetch a deployment
    sample_deployment = sch.deployments.get(deployment_name='Sample Deployment DC-DOCKER')

    # Update deployment name and tag/s
    sample_deployment.deployment_name = 'updated name'
    sample_deployment.tags = sample_deployment.tags + ['updatedTag']

    # Update stage libraries
    stage_libraries = sample_deployment.engine_configuration.stage_libs
    current_engine_version = sample_deployment.engine_configuration.engine_version
    if sample_deployment.engine_configuration.engine_type == 'DC':
        additional_stage_libs = ['jython_2_7', 'jdbc']
    else:
        additional_stage_libs = ['jdbc', 'snowflake-with-no-dependency']

    stage_libraries.extend(additional_stage_libs)

    # Update install type
    expected_install_type = 'DOCKER'
    sample_deployment.install_type = expected_install_type

    # Update external_resource_source
    expected_external_resource_source = 'http://www.google.com'
    sample_deployment.engine_configuration.external_resource_source = expected_external_resource_source

    # Update java configurations
    java_config = sample_deployment.engine_configuration.java_configuration
    java_config.maximum_java_heap_size_in_mb = 4096
    java_config.minimum_java_heap_size_in_mb = 2048
    java_config.java_options = '-Xdebug'

    # Update the deployment with all the above changes
    sch.update_deployment(sample_deployment)
