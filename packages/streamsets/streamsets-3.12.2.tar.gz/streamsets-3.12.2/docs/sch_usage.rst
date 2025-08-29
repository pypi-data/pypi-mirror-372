.. module:: streamsets
.. _sch_usage:
Control Hub Usage
==================
|
The following sections include explanations and examples of the extensive usage and implementation of the StreamSets SDK
for Python, specifically pertaining to the use of the SDK with StreamSets Control Hub.

If you are new to the SDK, we recommend that you first review the Data Collector usage documentation. Many of the original
and most fundamental concepts of the SDK are covered there, and much of the Control Hub documentation (and SDK
implementation, for that matter) builds upon this foundation.

Importing the ControlHub module
-------------------------------

The examples in this section assume you've installed the ``streamsets`` library,
:ref:`activated the library <activation>`, and are inside a Python 3.6+ interpreter.

You will also need access to a Control Hub instance, including a valid username and password for authenticating with
the Control Hub instance. In addition, most of the examples that follow assume that you have at least one Data Collector
instance registered with Control Hub that should be accessible by the Control Hub user credentials you provide.

Use of the SDK begins by importing the library. For convenience, we tend to directly import the classes we need:

.. code-block:: python

    from streamsets.sdk import ControlHub


.. toctree::
   :maxdepth: 2
   :hidden:

   usage/sch/connecting_to_sch
   usage/sch/creating_pipelines
   usage/sch/pipeline_labels
   usage/sch/pipeline_fragments
   usage/sch/import_export_pipelines
   usage/sch/preview_test_run
   usage/sch/connections
   usage/sch/connection_tags
   usage/sch/jobs
   usage/sch/job_templates
   usage/sch/job_tags
   usage/sch/scheduled_tasks
   usage/sch/topologies
   usage/sch/reports
   usage/sch/subscriptions
   usage/sch/provisioning_agents_deployments
   usage/sch/registered_data_collectors
   usage/sch/users
   usage/sch/groups
   usage/sch/acl
   usage/sch/login_action_audits
