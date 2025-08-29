Selecting stage libraries for a deployment is also possible using the SDK. The ``stage_libs`` property of the
:py:class:`streamsets.sdk.sch_models.DeploymentEngineConfiguration` attribute in a
Deployment object allows specification of additional stage libraries in the ``'<library_name>'`` format, or optionally
the ``'<library_name>:<library_version>'`` format.

.. note::
  If a version is omitted for a stage library, it will default to the engine version that was configured for the
  deployment.

There are several methods available for modifying the stage libraries of a deployment.
If you know the complete list of stage libraries you want to add to a deployment, you can specify them as a list
and set the ``stage_libs`` attribute directly as seen below:

.. warning::
  Attempting to add multiple versions of the same stage library to a deployment's engine configuration will result in
  an error when you attempt to add or update a deployment on the StreamSets Platform.

.. code-block:: python

    # Stage libraries can be supplied both with and without version specified. Any without a version will default
    # to the version of the engine selected for the deployment
    deployment.engine_configuration.stage_libs = ['jdbc', 'aws:4.1.0', 'cdp_7_1:4.1.0', 'basic:4.1.0', 'dev']

The ``stage_libs`` attribute operates like a traditional :py:obj:`list` object, with accompanying ``append()``,
``extend()``, and ``remove()`` methods.
If you are looking to add a single stage library to a deployment's engine configuration, you can utilize the
:py:meth:`streamsets.sdk.sch_models.DeploymentStageLibraries.append` method, using the same library:version syntax from
above:

.. code-block:: python

    # Adding a single additional library to the stage library configuration
    deployment.engine_configuration.stage_libs.append('aws')

If you would prefer to add a list of additional stage libraries to a deployment's engine configuration, you can utilize
the :py:meth:`streamsets.sdk.sch_models.DeploymentStageLibraries.extend` method, which also follows the same
library:version syntax from above:

.. code-block:: python

    # Extending the list of stage libraries by adding two additional stages
    deployment.engine_configuration.stage_libs.extend(['cassandra_3:4.1.0', 'elasticsearch_7'])

Finally, if you would like to remove a single stage library from a deployment's engine configuration, you can utilize
the :py:meth:`streamsets.sdk.sch_models.DeploymentStageLibraries.remove` method. The removal of a stage library from
a deployment's engine configuration intentionally requires a version to be supplied, so as to not accidentally remove
an unintended stage library:

.. code-block:: python

    # Removing a single library from the stage library configuration by supplying the library name and version
    deployment.engine_configuration.stage_libs.remove('aws:4.1.0')

Once the desired stage libraries have been set for the deployment, the deployment must be updated on Control Hub using
the :py:meth:`streamsets.sdk.ControlHub.update_deployment` method in order for them to take effect:

.. code-block:: python

    # Update a deployment's configuration/definition on Control Hub
    sch.update_deployment(deployment)
