Azure Environments
==================
|

When using a Microsoft Azure (Azure) environment, Control Hub connects to your Azure account, provisions the Azure
resources needed to run engines, and deploys engine instances to those resources.

Your Azure administrator must create an Azure virtual network (VNet) and configure Azure credentials for Control Hub to
use. You then create an Azure environment in Control Hub to connect to the existing VNet using these credentials.

While the environment is in an active state, Control Hub periodically verifies that the Azure VNet exists and that the
credentials are valid. Control Hub does not provision resources in the VNet until you create and start a deployment
for this environment.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Environments/Azure.html#concept_b5r_v3l_gqb>`_.

Creating Environment with Service Principal Client Secret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the UI workflow. This section shows you how to create an Azure environment with a Service
Principal Client Secret in the UI and how to achieve the same using StreamSets Platform SDK for Python
code step by step.

Define Environment
------------------

In the UI, an environment is defined as seen below:

.. image:: ../../../_static/images/set_up/environments/azure_environments/creation_define_environment.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='AZURE')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['azure-env-tag'],
                                            allow_nightly_builds=False)

Configure Azure Credentials
---------------------------

In the UI, the Azure credentials for an environment are configured as seen below:

.. image:: ../../../_static/images/set_up/environments/azure_environments/creation_configure_engine_configure_azure_credentials.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.credential_type = 'Service Principal Client Secret'
    environment.client_id = <azure client id>
    environment.client_secret = <azure client secret>
    environment.tenant_id = <azure tenant id>
    environment.subscription_id = <azure subscription id>

Select Azure Region
-------------------

In the UI, the Azure Region for an environment is selected as seen below:

.. image:: ../../../_static/images/set_up/environments/azure_environments/creation_configure_engine_configure_azure_region.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.region = 'westus2'

Configure Defaults for Azure VM Instances
-----------------------------------------

In the UI, the Defaults for Azure VM Instances for an environment are configured as seen below:

.. image:: ../../../_static/images/set_up/environments/azure_environments/creation_configure_engine_defaults_azure_vm_instances.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.default_managed_identity = <default managed identity>  # optional to set
    environment.default_resource_group = <default resource group>  # optional to set

Configure Azure VNet
--------------------

In the UI, the Azure VNet for an environment is configured as seen below:

.. image:: ../../../_static/images/set_up/environments/azure_environments/creation_configure_engine_configure_azure_vnet.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.vnet_id = '/subscriptions/c0955e10-a54b-4bf8-9bef-5377682c556e/resourceGroups/azure-csp/providers/Microsoft.Network/virtualNetworks/csp-vnet'
    environment.azure_tags = {'name1': 'value1', 'name2': 'value2'}

Configure Azure Subnet
----------------------

In the UI, the Azure Subnet for an environment is configured as seen below:

.. image:: ../../../_static/images/set_up/environments/azure_environments/creation_configure_engine_configure_azure_subnet.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    environment.subnet_id = '/subscriptions/c0955e10-a54b-4bf8-9bef-5377682c556e/resourceGroups/azure-csp/providers/Microsoft.Network/virtualNetworks/csp-vnet/subnets/default'
    environment.security_group_id = '/subscriptions/c0955e10-a54b-4bf8-9bef-5377682c556e/resourceGroups/azure-csp/providers/Microsoft.Network/networkSecurityGroups/csp-nsg'

Review & Activate
-----------------

In the UI, an environment can be reviewed and launched as seen below:

.. image:: ../../../_static/images/set_up/environments/azure_environments/creation_review_and_activate_environment.png

|

The same effect can be achieved by using the SDK as seen below:

.. code-block:: python

    sch.add_environment(environment)
    # Optional - equivalent to clicking on 'Activate & Exit'
    sch.activate_environment(environment)

Complete example with Service Principal Client Secret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

To create a new :py:class:`streamsets.sdk.sch_models.AzureEnvironment` object and add it to Control Hub, use the
:py:class:`streamsets.sdk.sch_models.EnvironmentBuilder` class.
Use the :py:meth:`streamsets.sdk.ControlHub.get_environment_builder` method to instantiate the builder object:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='AZURE')

Next, build the  environment by using :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build` method,
and pass the resulting environment object to the :py:meth:`streamsets.sdk.ControlHub.add_environment` method:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='AZURE')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['azure-env-tag'],
                                            allow_nightly_builds=False)
    environment.credential_type = 'Service Principal Client Secret'
    environment.client_id = <azure client id>
    environment.client_secret = <azure client secret>
    environment.tenant_id = <azure tenant id>
    environment.subscription_id = <azure subscription id>
    environment.region = 'westus2'
    environment.default_managed_identity = <default managed identity>  # optional to set
    environment.default_resource_group = <default resource group>  # optional to set

    environment.vnet_id = '/subscriptions/c0955e10-a54b-4bf8-9bef-5377682c556e/resourceGroups/azure-csp/providers/Microsoft.Network/virtualNetworks/csp-vnet'
    environment.azure_tags = {'name1': 'value1', 'name2': 'value2'}
    environment.subnet_id = '/subscriptions/c0955e10-a54b-4bf8-9bef-5377682c556e/resourceGroups/azure-csp/providers/Microsoft.Network/virtualNetworks/csp-vnet/subnets/default'
    environment.security_group_id = '/subscriptions/c0955e10-a54b-4bf8-9bef-5377682c556e/resourceGroups/azure-csp/providers/Microsoft.Network/networkSecurityGroups/csp-nsg'
