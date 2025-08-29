.. _Kubernetes Environments:

Kubernetes Environments
=======================
|

When using a Kubernetes environment, Control Hub generates a StreamSets Kubernetes agent install script and YAML definition that will create and launch the agent in your Kubernetes environment.
The Agent is responsible for provisioning Kubernetes resources needed to run engines and deploying engine instances to those resources.

Your Kubernetes administrator must complete several `prerequisites <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Environments/Kubernetes.html#concept_rxw_44g_2vb>`_ before you create a Kubernetes environment on Platform.

While the environment is in an active state, the StreamSets Kubernetes agent periodically checks with Control Hub to retrieve requests for provisioning resources.

For more details on Kubernetes environments, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Environments/Kubernetes.html#concept_l1w_h4g_2vb>`_.


Creating a Kubernetes Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|

The SDK is designed to mirror the workflow seen in the Platform UI.
This section shows you how to create a Kubernetes environment in the UI, and the step-by-step equivalent using the StreamSets Platform SDK for Python.

Define the Environment
----------------------

In the Platform UI, a Kubernetes environment can be defined using the wizard as seen below:

.. image:: ../../../_static/images/set_up/environments/kubernetes_environments/create_environment_wizard.png

|

The equivalent steps to define and create an environment using the SDK require that you retrieve an instance of :py:class:`streamsets.sdk.sch_models.EnvironmentBuilder`.
This can be done via the :py:meth:`streamsets.sdk.ControlHub.get_environment_builder` method, specifying the ``environment_type`` as ``'KUBERNETES'``.
Once the :py:class:`streamsets.sdk.sch_models.EnvironmentBuilder` instance has been retrieved, an environment can be created using the :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build` method and specifying key details like ``environment_name``, ``environment_tags``, or ``allow_nightly_builds``:

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='KUBERNETES')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['k8s-env-tag'],
                                            allow_nightly_builds=False)

Configure the Environment
-------------------------

In the Platform UI, a Kubernetes environment is configured using the wizard as seen below:

.. image:: ../../../_static/images/set_up/environments/kubernetes_environments/configure_environment_wizard.png

|

To configure a Kubernetes environment in the same way using the SDK, you can access the corresponding attributes for the newly built :py:class:`streamsets.sdk.sch_models.KubernetesEnvironment`:

.. code-block:: python

    environment.agent_version = '1.0.0'
    environment.kubernetes_namespace = 'Sample Environment'
    # environment.agent_java_options = '<java options to set on the agent - if desired>'
    environment.kubernetes_labels = {'environment': 'streamsets'}

Review & Activate
-----------------

Once you've completed configuration for a Kubernetes environment in the UI, you can activate the environment and generate the installation script as seen below:

.. image:: ../../../_static/images/set_up/environments/kubernetes_environments/activate_and_install_wizard.png

|

Clicking on ``Activate & Generate Install Script`` will generate an installation script similar to the following:

.. image:: ../../../_static/images/set_up/environments/kubernetes_environments/installation_script_wizard.png

|

To execute the same steps for a Kubernetes environment from the SDK, you'll first need to add the environment to Platform via the :py:meth:`streamsets.sdk.ControlHub.add_environment` method, passing in your newly-created environment.
Once the environment has been added, you can activate the environment using the :py:meth:`streamsets.sdk.ControlHub.activate_environment` method and passing in the environment:

.. code-block:: python

    sch.add_environment(environment)
    sch.activate_environment(environment)

Once the environment has been activated, you can now generate and retrieve the installation script for the Kubernetes agent that will be installed to your Kubernetes cluster.
Simply use the :py:meth:`streamsets.sdk.ControlHub.get_kubernetes_apply_agent_yaml_command` method, passing in your newly-created environment once again:

.. code-block:: python

    install_script = sch.get_kubernetes_apply_agent_yaml_command(environment)

Please refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Environments/Kubernetes.html#concept_l1w_h4g_2vb>`_ documentation for details on using the installation script with your Kubernetes cluster to install the agent.

With the above steps completed, you have successfully created and activated a new Kubernetes environment using the SDK!
To begin making use of the environment and deploying engines to it, check out the SDK documentation section on :ref:`Kubernetes Deployments`.

Bringing It All Together
------------------------

The complete scripts from this section can be found below. Commands that only served to verify some output from the
example have been removed.

.. code-block:: python

    environment_builder = sch.get_environment_builder(environment_type='KUBERNETES')
    environment = environment_builder.build(environment_name='Sample Environment',
                                            environment_tags=['k8s-env-tag'],
                                            allow_nightly_builds=False)
    environment.agent_version = '1.0.0'
    environment.kubernetes_namespace = 'Sample Environment'
    # environment.agent_java_options = '<java options to set on the agent - if desired>'
    environment.kubernetes_labels = {'environment': 'streamsets'}
    sch.add_environment(environment)
    sch.activate_environment(environment)
    install_script = sch.get_kubernetes_apply_agent_yaml_command(environment)
