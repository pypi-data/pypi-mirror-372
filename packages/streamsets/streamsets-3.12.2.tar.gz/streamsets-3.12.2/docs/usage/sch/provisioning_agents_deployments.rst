Provisioning Agents and Deployments
===================================
|
Control Hub allows you to automatically provision Data Collector containers on an orchestration framework, such as
Kubernetes.

A Provisioning Agent is a containerized application that runs in a Kubernetes container orchestration framework, and is
responsible for communicating with Control Hub to automatically provision Data Collector containers in the Kubernetes
cluster where it runs.

A Deployment is a logical grouping of Data Collector containers deployed by a Provisioning Agent to Kubernetes, all of
which are identical and highly available. The Provisioning Agent is then responsible for management of these containers.

The SDK allows for interaction with the Provisioning Agents and Deployments in Control Hub, including retrieving,
activating and deactivating Provisioning Agents, creating, retrieving, updating, starting and stopping Deployments, and
deleting both Provisioning Agents and Deployments.

Retrieving Provisioning Agents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve all provisioning agents that belong to your user's organization, you can reference the
:py:attr:`streamsets.sdk.ControlHub.provisioning_agents` attribute of your :py:class:`streamsets.sdk.ControlHub`
instance. You can also filter the results on attributes like ``name``, ``id``, and ``version``:

.. code-block:: python

    # Get all provisioning agents belonging to current organization
    sch.provisioning_agents

    # Get a particular provisioning agent
    sch.provisioning_agents.get(id='89A1B2D5-3994-449F-99EB-88CD58958C92')

    # Get all provisioning agents of version 3.19.1
    sch.provisioning_agents.get_all(version='3.19.1')

**Output:**

.. code-block:: python

    # sch.provisioning_agents
    [<ProvisioningAgent (id=89A1B2D5-3994-449F-99EB-88CD58958C92, name=minikube-control-agent, type=Kubernetes,
                         version=3.18.0)>]

    # sch.provisioning_agents.get(id='89A1B2D5-3994-449F-99EB-88CD58958C92')
    <ProvisioningAgent (id=89A1B2D5-3994-449F-99EB-88CD58958C92, name=minikube-control-agent, type=Kubernetes,
                        version=3.18.0)>

    # sch.provisioning_agents.get_all(version='3.19.1')
    [<ProvisioningAgent (id=679e3af0-32a9-4ee8-a217-1884d63accb6, name=rancher-deployment, type=Kubernetes, version=3.19.1)>,
     <ProvisioningAgent (id=BEB517CB-7D0D-4621-B312-37BA52DD5A46, name=sch-agent2, type=Kubernetes, version=3.19.1)>]

Deleting Provisioning Agents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To delete a provisioning agent, simply retrieve the :py:class:`streamsets.sdk.sch_models.ProvisioningAgent`
object you wish to delete and pass it to the :py:meth:`streamsets.sdk.ControlHub.delete_provisioning_agent` method:

.. code-block:: python

    provisioning_agent = sch.provisioning_agents.get(id='89A1B2D5-3994-449F-99EB-88CD58958C92')
    sch.delete_provisioning_agent(provisioning_agent)

Deactivating and Activating Provisioning Agents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Activation and deactivation of provisioning agents pertain to the authentication tokens used by the provisioning agents
for communication with Control Hub. When a provisioning agent is registered with an organization in Control Hub, it will
automatically generate an authentication token.

The SDK allows for activation and deactivation of the authentication tokens owned by provisioning agents through the
:py:meth:`streamsets.sdk.ControlHub.activate_provisioning_agent` and :py:meth:`streamsets.sdk.ControlHub.deactivate_provisioning_agent`
methods, respectively. Simply retrieve the :py:class:`streamsets.sdk.sch_models.ProvisioningAgent` object you want to
act on, and pass it to either function:

.. code-block:: python

    sch.activate_provisioning_agent(provisioning_agent)
    sch.deactivate_provisioning_agent(provisioning_agent)

Creating a new Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new deployment and add it to Control Hub, use the :py:class:`streamsets.sdk.sch_models.DeploymentBuilder`
class. Use the :py:meth:`streamsets.sdk.ControlHub.get_deployment_builder` method to instantiate the builder
object.

The deployment object can then be passed to the :py:meth:`streamsets.sdk.ControlHub.add_deployment` method to be
published in Control Hub:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder()

    # Get the provisioning agent to be used to manage this deployment
    provisioning_agent = sch.provisioning_agents.get(id='89A1B2D5-3994-449F-99EB-88CD58958C92')

    # Build the deployment with a name and description of 'from sdk', and the number of SDC instances set to 2
    deployment = deployment_builder.build(name='from sdk',
                                          provisioning_agent=provisioning_agent,
                                          number_of_data_collector_instances=2,
                                          description='from sdk')

    # Add the deployment to Control Hub
    sch.add_deployment(deployment)

Because there was no ``spec`` provided in the above :py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method,
the default deployment spec in Control Hub will be used. Alternatively if you wanted to use a custom YAML spec to build
the deployment, you can provide one directly:

.. code-block:: python

    deployment_builder = sch.get_deployment_builder()

    # Get the provisioning agent to be used to manage this deployment
    provisioning_agent = sch.provisioning_agents.get(id='89A1B2D5-3994-449F-99EB-88CD58958C92')

    # Open the YAML specification file for reading
    with open('deployment_spec.yaml') as f:
        deployment_spec = yaml.load(f)

    # Build the deployment with a name of description of 'from sdk with custom spec', the number of SDC instances
    # set to 1, and the custom YAML specification included
    deployment = deployment_builder.build(name='from sdk with custom spec',
                                          provisioning_agent=provisioning_agent,
                                          number_of_data_collector_instances=1,
                                          description='from sdk with custom spec',
                                          spec=deployment_spec)

    # Add the deployment to Control Hub
    sch.add_deployment(deployment)

Retrieving existing deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieving existing deployments is as simple as checking the :py:attr:`streamsets.sdk.ControlHub.deployments`
attribute for the :py:class:`streamsets.sdk.ControlHub` instance you're interested in:

.. code-block:: python

    sch.deployments

    # Get a particular deployment
    sch.deployments.get(id='329f8688-7458-4d4f-851c-fdfe548411b0:admin')

**Output:**

.. code-block:: python

    # sch.deployments
    [<Deployment (id=329f8688-7458-4d4f-851c-fdfe548411b0:admin, name=from sdk, number_of_data_collector_instances=2, status=INACTIVE)>,
     <Deployment (id=ff1be305-7488-43c6-853f-7829f499082e:admin, name=from sdk with custom spec, number_of_data_collector_instances=1,
                  status=INACTIVE)>]

    # sch.deployments.get(id='329f8688-7458-4d4f-851c-fdfe548411b0:admin')
    <Deployment (id=329f8688-7458-4d4f-851c-fdfe548411b0:admin, name=from sdk, number_of_data_collector_instances=2, status=INACTIVE)>

You can also look at the deployments a provisioning agent is responsible for by referencing the :py:attr:`streamsets.sdk.sch_models.ProvisioningAgent.deployments`
attribute of a :py:class:`streamsets.sdk.sch_models.ProvisioningAgent` instance:

.. code-block:: python

    provisioning_agent.deployments

**Output:**

.. code-block:: python

    [<Deployment (id=329f8688-7458-4d4f-851c-fdfe548411b0:admin, name=from sdk, number_of_data_collector_instances=2, status=INACTIVE)>,
     <Deployment (id=ff1be305-7488-43c6-853f-7829f499082e:admin, name=from sdk with custom spec, number_of_data_collector_instances=1,
                  status=INACTIVE)>]

Starting a deployment
~~~~~~~~~~~~~~~~~~~~~

Once a deployment is added to Control Hub, it must be started in order for the Data Collector containers to be spun up
by the provisioning agent. To start a deployment, retrieve the :py:class:`streamsets.sdk.sch_models.Deployment` object
to be started and pass it to the :py:meth:`streamsets.sdk.ControlHub.start_deployment` method:

.. code-block:: python

    deployment = sch.deployments.get(id='329f8688-7458-4d4f-851c-fdfe548411b0:admin')
    sch.start_deployment(deployment)

Scaling an active deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As with any deployment on a containerization framework, Control Hub allows you to scale deployments up and down to meet
the needs of your use case. To scale a deployment, retrieve the :py:class:`streamsets.sdk.sch_models.Deployment`
object to be modified, and then pass it to the :py:meth:`streamsets.sdk.ControlHub.scale_deployment` method along with
the number of Data Collector instances to scale the deployment to:

.. code-block:: python

    deployment = sch.deployments.get(name='from sdk')
    sch.scale_deployment(deployment, num_instances=2)

Stopping a deployment
~~~~~~~~~~~~~~~~~~~~~

Stopping a deployment is identical to starting a deployment. Retrieve the :py:class:`streamsets.sdk.sch_models.Deployment`
object to be stopped and pass it to the :py:meth:`streamsets.sdk.ControlHub.stop_deployment` method.
In the example below, we attempt to stop a deployment within a try/catch in case the deployment in question becomes
inactive - at which point the :py:meth:`streamsets.sdk.ControlHub.acknowledge_deployment_error` method is used to
acknowledge the inactive error, and put the deployment into an ``inactive`` state (as it would be when successfully
stopped):

.. code-block:: python

    from streamsets.sdk.exceptions import DeploymentInactiveError
    try:
        sch.stop_deployment(deployment)
    except DeploymentInactiveError:
        sch.acknowledge_deployment_error(deployment)

Updating an existing deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deployments can also be updated directly via the SDK. Attributes like ``name``, ``number_of_data_collectors``, and even
``spec`` can be modified for a given deployment. Simply retrieve the :py:class:`streamsets.sdk.sch_models.Deployment`
object you'd like to modify, make the desired changes to it, and then pass the modified object to the
:py:meth:`streamsets.sdk.ControlHub.update_deployment` method:

.. code-block:: python

    deployment = sch.deployments.get(name='from sdk')
    deployment.name = 'a new deployment name'
    sch.update_deployment(deployment)
    sch.deployments.get(name='a new deployment name')

**Output:**

.. code-block:: python

    # sch.update_deployment(deployment)
    <streamsets.sdk.sch_api.Command object at 0x7f42da3cbb00>

    # sch.deployments.get(name='a new deployment name')
    <Deployment (id=329f8688-7458-4d4f-851c-fdfe548411b0:admin, name=a new deployment name, number_of_data_collector_instances=2, status=INACTIVE)>

Deleting existing deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK also enables you to delete deployments as required. You can delete a single deployment, or multiple deployments,
by using the :py:meth:`streamsets.sdk.ControlHub.delete_deployment` method:

.. code-block:: python

    # Delete a single deployment
    deployment = sch.deployments.get(name='from sdk')
    sch.delete_deployment(deployment)

    # Delete multiple deployments
    deployments = sch.deployments.get_all(number_of_data_collector_instances=1)
    sch.delete_deployment(*deployments)

