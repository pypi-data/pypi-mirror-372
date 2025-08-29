StreamSets Control Hub
======================

.. module:: streamsets.sdk.sch_models
.. module:: streamsets.sdk.ControlHub

Main interface
""""""""""""""
This is the main entry point used by users when interacting with SCH instances.

.. autoclass:: streamsets.sdk.ControlHub
    :members:

Models
""""""
These models wrap and provide useful functionality for interacting with common SCH abstractions.

ACLs
^^^^
.. autoclass:: streamsets.sdk.sch_models.ACL
    :members:
.. autoclass:: streamsets.sdk.sch_models.ACLPermissionBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.Permission
    :members:

Alerts
^^^^^^
.. autoclass:: streamsets.sdk.sch_models.Alert
    :members:

Classifiers
^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.Classifier
    :members:

Classification Rules
^^^^^^^^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.ClassificationRule
    :members:
.. autoclass:: streamsets.sdk.sch_models.ClassificationRuleBuilder
    :members:

Connections
^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.Connection
    :members:
.. autoclass:: streamsets.sdk.sch_models.Connections
    :members:
.. autoclass:: streamsets.sdk.sch_models.ConnectionBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.ConnectionVerificationResult
    :members:

DataCollectors
^^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.DataCollector
    :members:

Transformers
^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.Transformer
    :members:

Group
^^^^^
.. autoclass:: streamsets.sdk.sch_models.Group
    :members:
.. autoclass:: streamsets.sdk.sch_models.Groups
    :members:
.. autoclass:: streamsets.sdk.sch_models.GroupBuilder
    :members:

Jobs
^^^^
.. autoclass:: streamsets.sdk.sch_models.Job
    :members:
.. autoclass:: streamsets.sdk.sch_models.Jobs
    :members:
.. autoclass:: streamsets.sdk.sch_models.JobBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.JobMetrics
    :members:
.. autoclass:: streamsets.sdk.sch_models.JobOffset
    :members:
.. autoclass:: streamsets.sdk.sch_models.JobRunEvent
    :members:
.. autoclass:: streamsets.sdk.sch_models.JobStatus
    :members:
.. autoclass:: streamsets.sdk.sch_models.JobTimeSeriesMetric
    :members:
.. autoclass:: streamsets.sdk.sch_models.JobTimeSeriesMetrics
    :members:
.. autoclass:: streamsets.sdk.sch_models.RuntimeParameters
    :members:

Organizations
^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.Organization
    :members:
.. autoclass:: streamsets.sdk.sch_models.Organizations
    :members:
.. autoclass:: streamsets.sdk.sch_models.OrganizationBuilder
    :members:

Pipelines
^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.Pipeline
    :members:
.. autoclass:: streamsets.sdk.sch_models.Pipelines
    :members:
.. autoclass:: streamsets.sdk.sch_models.PipelineBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.PipelineCommit
    :members:
.. autoclass:: streamsets.sdk.sch_models.PipelineLabel
    :members:
.. autoclass:: streamsets.sdk.sch_models.PipelineLabels
    :members:
.. autoclass:: streamsets.sdk.sch_models.PipelineParameters
    :members:
.. autoclass:: streamsets.sdk.sch_models.StPipelineBuilder
    :members:

Protection Methods
^^^^^^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.ProtectionMethod
    :members:
.. autoclass:: streamsets.sdk.sch_models.ProtectionMethodBuilder
    :members:

Protection Policies
^^^^^^^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.ProtectionPolicy
    :members:
.. autoclass:: streamsets.sdk.sch_models.ProtectionPolicies
    :members:
.. autoclass:: streamsets.sdk.sch_models.ProtectionPolicyBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.PolicyProcedure
    :members:

ProvisioningAgents
^^^^^^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.Deployment
    :members:
.. autoclass:: streamsets.sdk.sch_models.Deployments
    :members:
.. autoclass:: streamsets.sdk.sch_models.DeploymentBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.ProvisioningAgent
    :members:
.. autoclass:: streamsets.sdk.sch_models.ProvisioningAgents
    :members:

Reports
^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.GenerateReportCommand
    :members:
.. autoclass:: streamsets.sdk.sch_models.Report
    :members:
.. autoclass:: streamsets.sdk.sch_models.Reports
    :members:
.. autoclass:: streamsets.sdk.sch_models.ReportDefinition
    :members:
.. autoclass:: streamsets.sdk.sch_models.ReportDefinitions
    :members:
.. autoclass:: streamsets.sdk.sch_models.ReportDefinitionBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.ReportResource
    :members:
.. autoclass:: streamsets.sdk.sch_models.ReportResources
    :members:

Scheduler
^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.ScheduledTask
    :members:
.. autoclass:: streamsets.sdk.sch_models.ScheduledTaskAudit
    :members:
.. autoclass:: streamsets.sdk.sch_models.ScheduledTaskBaseModel
    :members:
.. autoclass:: streamsets.sdk.sch_models.ScheduledTaskBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.ScheduledTaskRun
    :members:
.. autoclass:: streamsets.sdk.sch_models.ScheduledTasks
    :members:

Subscriptions
^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.Subscription
    :members:
.. autoclass:: streamsets.sdk.sch_models.Subscriptions
    :members:
.. autoclass:: streamsets.sdk.sch_models.SubscriptionAction
    :members:
.. autoclass:: streamsets.sdk.sch_models.SubscriptionAudit
    :members:
.. autoclass:: streamsets.sdk.sch_models.SubscriptionBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.SubscriptionEvent
    :members:

Topologies
^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.DataSla
    :members:
.. autoclass:: streamsets.sdk.sch_models.DataSlaBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.Topology
    :members:
.. autoclass:: streamsets.sdk.sch_models.Topologies
    :members:
.. autoclass:: streamsets.sdk.sch_models.TopologyBuilder
    :members:
.. autoclass:: streamsets.sdk.sch_models.TopologyNode
    :members:

Users
^^^^^
.. autoclass:: streamsets.sdk.sch_models.User
    :members:
.. autoclass:: streamsets.sdk.sch_models.Users
    :members:
.. autoclass:: streamsets.sdk.sch_models.UserBuilder
    :members:

Common
------
Models used by StreamSets Data Collector and StreamSets Control Hub:

.. autoclass:: streamsets.sdk.models.Configuration
    :members:

Exceptions
----------

.. automodule:: streamsets.sdk.exceptions
    :members:
