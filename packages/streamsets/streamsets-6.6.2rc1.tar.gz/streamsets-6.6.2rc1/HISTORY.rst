  .. warning::
    Support for Python versions below 3.8 will be dropped in the next major release of Streamsets SDK (7.0.0)

History
=======
6.6.1 (June 2025)
----------------------
* Fixed an issue that caused an error to be raised when calling the method :py:meth:`streamsets.sdk.ControlHub.delete_deployment`.

* Bug fixes and improvements

6.6.0 (June 2025)
-----------------
* Added support for interacting with network access rules

    * Added the ability to modify whether network access rules are enabled for your organization using the :py:attr:`streamsets.sdk.sch_models.Organization.ip_auth_enabled` attribute.

    * Added the ability to modify network access rules for your organization using the :py:meth:`streamsets.sdk.sch_models.Organization.add_ip_auth_ruleset` and :py:meth:`streamsets.sdk.sch_models.Organization.remove_ip_auth_ruleset`.

    * Added the ability to view the current network access rules using the :py:attr:`streamsets.sdk.sch_models.Organization.ip_auth_rules` attribute.

* Added functionality to check the possible values of a stage configuration by using the :py:meth:`streamsets.sdk.sch_models.PipelineBuilder.get_stage_configuration_options` method.

* Added support for interacting with Projects

    * Added SDK support for projects feature by being able to switch between different projects using the :py:attr:`streamsets.sdk.ControlHub.current_project` attribute.

    * Added SDK support to list and modify projects by using the :py:attr:`streamsets.sdk.ControlHub.projects` attribute and the methods :py:meth:`streamsets.sdk.ControlHub.add_project` and :py:meth:`streamsets.sdk.ControlHub.delete_project`.

* Bug fixes and improvements.

6.5.0 (November 2024)
-----------------
* The :py:class:`streamsets.sdk.sch_models.Step` class now supports Finish Conditions and has a new attribute ``name`` which will allow retrieving and setting the name of a step.

* Added support for running an arbitrary step using the The :py:meth:`streamsets.sdk.ControlHub.run_job_sequence` method.

* Extended AQL functionality to now support searching on :py:class:`streamsets.sdk.sch_models.JobSequence` objects.

* Updated API calls to be more efficient by changing the default page size to `250` instead of `50`.

* Added SDK support for creating connections without an authoring engine specified (engineless connections).

* Added SDK support for stopping a Deployment through the :py:meth:`streamsets.sdk.ControlHub.delete_deployment` method.

* Added the ability to specify the ``install_type`` for a self-managed deployment when retrieving the install script.

* Bug fixes and improvements.

6.4.0 (July 2024)
-----------------
* Added :py:meth:`streamsets.sdk.ControlHub.clone_deployment` method to easily a clone a deployment.

* Added :py:meth:`streamsets.sdk.ControlHub.get_kubernetes_environment_yaml` method to fetch a Kubernetes environment's YAML.

* Added :py:meth:`streamsets.sdk.sch_models.Pipeline.add_fragment` method which lets users add fragments to existing pipelines.

* Added :py:meth:`streamsets.sdk.sch_models.Pipeline.get_jobs_using_pipeline` method which returns all the jobs that use the pipeline.

* Added :py:meth:`streamsets.sdk.sch_models.JobSequence.delete_history_logs` method which can delete history logs for the job sequence.

* Resolved a bug that did not let users update permissions for deployments correctly.

* Bug fixes and improvements.

6.3.0 (May 2024)
----------------
* The :py:meth:`streamsets.sdk.ControlHub.get_self_managed_deployment_install_script` method now accepts a parameter ``java_version`` that can be used to specify which java version to be used when generating an install script.

* The :py:meth:`streamsets.sdk.ControlHub.add_scheduled_task` method raises a more detailed error when creating a :py:class:`streamsets.sdk.sch_models.ScheduledTask`object.

* Support for Job Sequencing has been added. Refer to the :ref:`StreamSets SDK Job Sequencing Documentation <job_sequences>` for further details.

* Bug fixes and improvements.

6.2.0 (February 2024)
---------------------
* The :py:meth:`streamsets.sdk.ControlHub.verify_connection` method now accepts a parameter ``library`` that can be used to specify which library the connection should be verified against.

* The :py:meth:`streamsets.sdk.ControlHub.publish_pipeline` method now accepts a parameter ``validate`` which can be used to validate a pipeline when saving it on Platform.

* The :py:meth:`streamsets.sdk.sch_models.PipelineBuilder.build` method now accepts a parameter ``description`` which can be used to set the description of a pipeline.

* The :py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` method now accepts additional parameters that can be used to configure the deployment during creation.

* The :py:class:`streamsets.sdk.sch_models.Job` class has a new attribute ``latest_committed_offsets`` which will retrieve latest committed offsets for the Job.

* Fixed an error that did not render color icons in the Platform UI for pipelines generated in the SDK.

* Fixed an error with :py:meth:`streamsets.sdk.ControlHub.activate_api_credential`, :py:meth:`streamsets.sdk.ControlHub.deactivate_api_credential` and :py:meth:`streamsets.sdk.ControlHub.rename_api_credential` that caused the authentication token to be regenerated.

* Bug fixes and improvements.

6.1.0 (November 2023)
---------------------
* Allow direct replacement of a stage in a pipeline. This is achieved through the ``copy_inputs`` & ``copy_outputs`` methods under the :py:class:`streamsets.sdk.sch_models.SchSdcStage` and :py:class:`streamsets.sdk.sch_models.SchStStage` classes respectively.

* Service configurations for Stages have now been re-homed under the ``configuration`` stage attribute. However, service configurations for Stages will continue to be accessible via the ``services`` attribute.

* The :py:class:`streamsets.sdk.sch_models.Connection` class's configuration attributes have now been pythonized.

* Fixed bug related to the :py:meth:`streamsets.sdk.ControlHub.update_scheduled_task` method.

* Fixed recursion issue with deep-copying :py:class:`streamsets.sdk.sch_models.SchSdcStage` and :py:class:`streamsets.sdk.sch_models.SchStStage` instances.

* Fixed inconsistency with unsupported connections being added to existing stages.

* Fixed issue where Monitor Job view did not render pipeline stages added using the SDK.

* Bug fixes and improvements.

6.0.1 (September 2023)
----------------------
* Fixed an issue that caused output lanes to be duplicated for :py:class:`streamsets.sdk.sch_models.SchSdcStage` or :py:class:`streamsets.sdk.sch_models.SchStStage` instances (only for ``Stream Selector`` stages).

* Bug fixes and improvements

6.0.0 (August 2023)
-------------------
* Existing pipelines and their stages are now directly editable from the SDK. Previously the SDK only supported creation of new Pipelines and publishing those to the Platform for the first time. With this change, instances of :py:class:`streamsets.sdk.sch_models.SchSdcStage` and :py:class:`streamsets.sdk.sch_models.SchStStage` can be added, removed, replaced, connected and disconnected using only the SDK - enabling programmatic pipeline editing at scale.

* Top level configurations for :py:class:`streamsets.sdk.sch_models.Pipeline`, :py:class:`streamsets.sdk.sch_models.SchSdcStage`, and :py:class:`streamsets.sdk.sch_models.SchStStage` have begun to be moved under the ``configuration`` attribute. The configuration properties will still be accessible as top-level attributes until the next major release.

* Setting :py:attr:`streamsets.sdk.st_models.Stage.output_lanes` or :py:attr:`streamsets.sdk.sdc_models.Stage.output_lanes` is now deprecated.

* The :py:class:`streamsets.sdk.sch_models.SchSdcStage` ``Stream Selector`` has been updated to not require ``outputLane`` while defining ``predicates``.

  .. note::
    While heavily discouraged, it is still possible to define a particular ``outputLane`` for each of the ``predicates`` to avoid inconsistencies.

* :py:class:`streamsets.sdk.sch_models.ScheduledTask` actions are now refactored under :py:class:`streamsets.sdk.ControlHub`.

  .. warning::
    This will affect usage of SDK and the following functions have been removed and replaced:
    :py:meth:`streamsets.sdk.sch_models.ScheduledTask.resume`, :py:meth:`streamsets.sdk.sch_models.ScheduledTask.pause`, :py:meth:`streamsets.sdk.sch_models.ScheduledTask.kill` and :py:meth:`streamsets.sdk.sch_models.ScheduledTask.delete`
    are now replaced by :py:meth:`streamsets.sdk.ControlHub.resume_scheduled_tasks`, :py:meth:`streamsets.sdk.ControlHub.pause_scheduled_tasks`, :py:meth:`streamsets.sdk.ControlHub.kill_scheduled_tasks` and :py:meth:`streamsets.sdk.ControlHub.delete_scheduled_tasks` respectively.

    Please refer to the documentation for the correct, updated usage.

* :py:meth:`streamsets.sdk.sch_models.PipelineBuilder.import_pipeline` has been refactored to accept a parameter of type :py:class:`streamsets.sdk.sch_models.Pipeline` instead of a :py:obj:`dict` of pipeline definitions. This allows using an existing pipeline as the base for creating a new pipeline via the :py:class:`streamsets.sdk.sch_models.PipelineBuilder` class.

* :py:attr:`streamsets.sdk.ControlHub.engine_configurations` has been refactored to :py:attr:`streamsets.sdk.ControlHub.engine_versions`.

* Deployment attribute :py:attr:`streamsets.sdk.sch_models.Deployment.engine_instances` has been renamed to :py:attr:`streamsets.sdk.sch_models.Deployment.desired_instances`

* Bug fixes and improvements

5.2.1 (May 2023)
----------------
* Fixed a TypeError Exception when filtering jobs by status in ControlHub.

5.2.0 (April 2023)
---------------------
* Support for Kubernetes Environments and Deployments has been added. Refer
  to the :ref:`StreamSets SDK Deployments Usage Documentation <Kubernetes Deployments>` or :ref:`StreamSets SDK Environments Usage Documentation <Kubernetes Environments>` for further details.

* Support for SAQL (StreamSets Advanced Query Language) Saved Searches has been added. Refer to the :ref:`StreamSets Search Documentation <saql_saved_searches>` for further details.

* Support for Draft Runs has been added. Refer to the :ref:`StreamSets SDK Run Documentation <draft_runs>` for further details.

* The :py:meth:`streamsets.sdk.ControlHub.Jobs.get_all` method now supports filtering by the ``job_id`` parameter.

* The :py:class:`streamsets.sdk.sch_models.EC2Deployment` class directly uses the default instance profile of its :py:class:`streamsets.sdk.sch_models.AWSEnvironment` class

* Bug fixes and improvements.

5.1.0 (December 2022)
---------------------
* Support for StreamSets Advanced Query Language has been added for Pipelines, Fragments, and Jobs. Refer
  to the :ref:`StreamSets SDK Search Documentation <search_for_objects>` for further details.

* The :py:meth:`streamsets.sdk.ControlHub.engines.get_all` method now supports filtering by the ``id`` parameter.

* Bug fixes and improvements.

5.0.0 (August 2022)
-------------------
* The :py:meth:`streamsets.sdk.ControlHub.validate_pipeline` method now supports validating SDC and Transformer
  pipelines.

* Changing the name of a :py:class:`streamsets.sdk.sch_models.Pipeline` instance is now possible by setting the ``name``
  attribute of the instance and passing it to :py:meth:`streamsets.sdk.ControlHub.publish_pipeline`.

* Improved the usability of the :py:class:`streamsets.sdk.sch_models.ApiCredentialBuilder` class and its interaction
  with the :py:meth:`streamsets.sdk.ControlHub.add_api_credential` method.

  .. note::
    Please refer to the documentation for the correct, updated usage.

* The :py:class:`streamsets.sdk.sch_models.User` and :py:class:`streamsets.sdk.sch_models.Group` classes have received
  several improvements including:

  * The :py:attr:`streamsets.sdk.sch_models.User.groups` and :py:attr:`streamsets.sdk.sch_models.Group.users` attributes
    have been improved to return :py:class:`streamsets.sdk.sch_models.Group` and :py:class:`streamsets.sdk.sch_models.User`
    instances (respectively) rather than just ID values.

  .. warning::
     This will affect existing SDK usage of the :py:attr:`streamsets.sdk.sch_models.User.groups` and
     :py:attr:`streamsets.sdk.sch_models.Group.users` attributes. Please refer to the documentation for the correct,
     updated usage.

* The :py:class:`streamsets.sdk.sch_models.DataCollector` and :py:class:`streamsets.sdk.sch_models.Transformer` classes
  have been refactored into a single class which houses the functionality for both:
  :py:class:`streamsets.sdk.sch_models.Engine`. Subsequently, the :py:attr:`streamsets.sdk.ControlHub.data_collectors`
  and :py:attr:`streamsets.sdk.ControlHub.transformers` attributes now utilize the :py:class:`streamsets.sdk.sch_models.Engines`
  class instead.

  .. warning::
     This will affect existing SDK usage of the :py:attr:`streamsets.sdk.ControlHub.data_collectors` and
     :py:attr:`streamsets.sdk.ControlHub.transformers` attributes, as these will both now return instances of the
     :py:class:`streamsets.sdk.sch_models.Engine` class. Please refer to the documentation for the correct,
     updated usage.

* Pagination improvements have been made for various classes

* When retrieving :py:class:`streamsets.sdk.sch_models.Job` instances via :py:attr:`streamsets.sdk.ControlHub.jobs` and supplying a ``job_tag`` value, including the organization that the job tag belongs to is no longer required.

  .. warning::
     This will affect existing SDK usage of the :py:attr:`streamsets.sdk.ControlHub.jobs` attribute. Please refer to the documentation for the correct, updated usage.

* Arguments and attributes that were marked as deprecated in the previous release have been removed.

* Bug fixes and improvements


4.3.0 (August 2022)
-------------------
* Added support for using the SDK on Python 3.10

* :py:class:`streamsets.sdk.sch_models.Users` and :py:class:`streamsets.sdk.sch_models.Groups` instances can now be
  filtered on specific text values via the ``filter_text`` parameter, as seen in the UI

* Bug fixes and improvements


4.2.1 (July 2022)
-----------------
* Fixes a bug when trying to modify or update a :py:class:`streamsets.sdk.sch_models.ACL` definition for :py:class:`streamsets.sdk.sch_models.Deployment`
  instances.

* Fixes a bug in the naming convention used for pipelines created via the :py:meth:`streamsets.sdk.ControlHub.test_pipeline_run`
  method.

* Fixes a bug that prevented users from supplying a ``'.'`` (period) character in the ``group_id`` when creating a group
  via the :py:meth:`streamsets.sdk.sch_models.GroupBuilder.build` method.


4.2.0 (May 2022)
----------------
* Programmatic User creation and management has been added

* Pagination and "lazy" loading improvements have been made to various classes

* The Group class has been refactored slightly to better match the experience seen in the UI

.. note::
  When filtering the :py:class:`streamsets.sdk.sch_models.Groups` objects in StreamSets Platform, the ``id`` argument has
  been replaced by ``group_id`` to match the :py:class:`streamsets.sdk.sch_models.Group` class's representation. Please
  refer to the documentation for the correct, updated usage.

* The :py:meth:`streamsets.sdk.sch_models.DeploymentBuilder.build` and :py:meth:`streamsets.sdk.sch_models.EnvironmentBuilder.build`
  methods no longer require the ``deployment_type`` or ``environment_type`` arguments to be supplied

.. warning::
  The ``deployment_type`` and ``environment_type`` arguments are deprecated and will be removed in a future release.
  Please refer to the documentation for the correct, updated usage.

* The :py:class:`streamsets.sdk.sch_models.Deployments` and :py:class:`streamsets.sdk.sch_models.Environments` classes
  can now be filtered on ``deployment_id`` and ``environment_id`` respectively, instead of ``id``

.. warning::
  The ``id`` argument has been deprecated and will be removed in a future release. Please refer to the documentation for
  the correct, updated usage.


4.1.0 (March 2022)
--------------------
* Modified error handling to return all errors returned by an API call to StreamSets Platform

* Transformer for Snowflake support

* Support for nightly builds of execution engines


4.0.0 (January 2022)
--------------------
* Activation key is no longer required

* DataCollector and Transformer classes are no longer public because these are headless engines in StreamSets Platform

* Authentication is now handled using API Credentials

* The usage and syntax for PipelineBuilder has been updated

* Support for environments and deployments

