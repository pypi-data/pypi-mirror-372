StreamSets Transformer
======================

.. module:: streamsets.sdk.Transformer

Main interface
""""""""""""""
This is the main entry point used by users when interacting with Transformer instances.

.. autoclass:: streamsets.sdk.Transformer
    :members:

Models
""""""
These models wrap and provide useful functionality for interacting with common SCH abstractions.

Alerts
^^^^^^
.. autoclass:: streamsets.sdk.st_models.Alert
    :members:
.. autoclass:: streamsets.sdk.st_models.Alerts
    :members:

Data Rules
^^^^^^^^^^
.. autoclass:: streamsets.sdk.st_models.DataDriftRule
    :members:
.. autoclass:: streamsets.sdk.st_models.DataRule
    :members:

History
^^^^^^^
.. autoclass:: streamsets.sdk.st_models.History
    :members:
.. autoclass:: streamsets.sdk.st_models.HistoryEntry
    :members:

Issues
^^^^^^
.. autoclass:: streamsets.sdk.st_models.Issue
    :members:
.. autoclass:: streamsets.sdk.st_models.Issues
    :members:

Logs
^^^^
.. autoclass:: streamsets.sdk.st_models.Log
    :members:

Metrics
^^^^^^^
.. autoclass:: streamsets.sdk.st_models.MetricCounter
    :members:
.. autoclass:: streamsets.sdk.st_models.MetricGauge
    :members:
.. autoclass:: streamsets.sdk.st_models.MetricHistogram
    :members:
.. autoclass:: streamsets.sdk.st_models.MetricTimer
    :members:
.. autoclass:: streamsets.sdk.st_models.Metrics
    :members:

Pipelines
^^^^^^^^^
.. autoclass:: streamsets.sdk.st_models.PipelineBuilder
    :members:
.. autoclass:: streamsets.sdk.st_models.Pipeline
    :members:
.. autoclass:: streamsets.sdk.st_models.Stage
    :members:

Pipeline ACLs
^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.st_models.PipelineAcl
    :members:

Pipeline Permissions
^^^^^^^^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.st_models.PipelinePermission
    :members:
.. autoclass:: streamsets.sdk.st_models.PipelinePermissions
    :members:

Previews
^^^^^^^^
.. autoclass:: streamsets.sdk.st_models.Preview
    :members:

Snapshots
^^^^^^^^^
.. autoclass:: streamsets.sdk.st_models.Batch
    :members:
.. autoclass:: streamsets.sdk.st_models.Record
    :members:
.. autoclass:: streamsets.sdk.st_models.RecordHeader
    :members:
.. autoclass:: streamsets.sdk.st_models.StageOutput
    :members:

Users
^^^^^
.. autoclass:: streamsets.sdk.st_models.User
    :members: