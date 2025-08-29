3.12.2 (2025.08.29)
-------------------

* Added support for Python 3.10 and newer

* Dropped support for Python versions earlier than 3.6

3.12.1 (2022.04.08)
-------------------

* Updated pagination handling for Topology and ScheduledTask API endpoints.

* Bug fixes and improvements.

3.12.0 (2022.02.24)
-------------------

* Accessing :py:class:`streamsets.sdk.ControlHub` objects (i.e. Deployments, Topologies, Connections) should be faster
  and more responsive.

* Added support for modifying the cron expression for Scheduled Tasks.

* Using ``dir()`` on various SDK classes/objects should return a more complete list of available attributes.

* Documentation updates, including a new install command that will pull the latest release of the 3.x SDK.

* Bug fixes and improvements.

3.11.0 (2021.10.15)
-------------------

* Support for Topologies has been expanded to allow full functionality from the SDK including:

  * Creating Topologies from scratch.

  * Modifying nodes within a Topology (adding/removing nodes).

  * Topology maintenance (auto-fixing, auto-discovering connections, validation issues).

  * Upgrading jobs to their latest pipeline version directly from a topology.
  .. warning::
    This will affect existing SDK usage of some methods previously contained under the :py:class:`streamsets.sdk.ControlHub`
    class that pertained to Topologies, as they have been moved under the :py:class:`streamsets.sdk.sch_models.Topology`
    class to match the proper scope. Please refer to the :ref:`Topology documentation <topologies>` for the correct,
    updated usage.
* Support for Control Hub's paginated APIs has been added.
* Bug fixes and improvements.
* The SDK documentation has been reorganized and rewritten for improved usability.


3.10.1 (2021.06.18)
-------------------

* Bug fix.

3.10.0 (2021.04.30)
-------------------

* Support for Subscription Audits in Control Hub has been added.
* Support for Data SLAs within Control Hub Topologies has been added.
* Support for ACL access for multiple resources has been added (Topologies, Subscriptions, Scheduled Tasks, Deployments).
* Support for Control Hub Alerts has been added.
* SDC pipeline snapshots have been refactored, and now match much more closely to what's seen in the SDC UI.
    .. warning::
        This will affect existing SDK usage of the :py:class:`streamsets.sdk.sdc_models.Snapshot` class. Upgrading to
        the 3.10.0 release without modifying existing code to use the new syntax will result in execution failures.
        Please refer to the
        `Snapshot documentation <https://streamsets.com/documentation/sdk/latest/usage/sdc/pipeline_snapshots.html>`_
        for the correct, updated usage.

* Metrics for Control Hub jobs have been refactored to show metrics counts for all runs of a given job, and now also match much more closely to what's seen in the Control Hub UI.
    .. warning::
        This will affect existing SDK usage of the :py:class:`streamsets.sdk.sch_models.JobMetrics` class. Upgrading to
        the 3.10.0 release without modifying existing code to use the new syntax will result in execution failures.
        Please refer to the
        `Metrics documentation <https://streamsets.com/documentation/sdk/latest/usage/sch/jobs.html#metrics>`_
        for the correct, updated usage.
* Bug fixes and improvements.

3.9.0 (2021.01.13)
------------------

* Support for Connection Catalog in Control Hub.
* Support for Control Hub Job Tags.
* Support for StreamSets Accounts.

3.8.0 (2020.06.30)
------------------

* Support for faster loading of Control Hub pipelines.
* Support pagination for Control Hub pipelines and jobs.
* Support for managing Control Hub pipeline labels.
* Bug fixes and improvements.

3.7.1 (2020.04.22)
------------------

* Bug fix.

3.7.0 (2020.02.03)
------------------

* Support for Python 3.7 and Python 3.8.
* Support for specifying activation key through environment variable.
* Bug fixes and improvements.

3.6.1 (2019.10.25)
------------------

* Add missing support for updating existing pipeline in Control Hub by importing JSON file.

3.6.0 (2019.10.17)
------------------

* Support for Transformer
* Support for Control Hub Deployments
* Bug fixes and improvements.

3.5.0 (2019.06.27)
------------------

* Expand StreamSets Control Hub functionality to include features like Pipeline Fragments, Job History, User Groups.
* Bug fixes and improvements.


3.4.0 (2019.04.04)
------------------

* Expand StreamSets Control Hub functionality to include features like Scheduler, import/export pipelines.
* Expand StreamSets Data Collector functionality to include and improve import/export pipelines.
* Bug fixes and improvements.


3.3.0 (2019.02.20)
------------------

* Expand StreamSets Control Hub functionality heavily.
* Expand StreamSets Data Collector functionality.
* Bug fixes and improvements.

3.2.0 (2018.05.10)
------------------

* Expand functionality to include more StreamSets Data Collector functionality.

1.2.1 (2017.12.15)
------------------

* Fix bug in Sqoop Import tool when using compression.

1.2.0 (2017.12.08)
------------------

* Added basic support for services in stage instance definition.
* Improved Sqoop Import tool command line options.

1.1.0 (2017.09.20)
------------------

* Added Sqoop Import tool.

1.0.0 (2017.08.31)
------------------

* First release.
