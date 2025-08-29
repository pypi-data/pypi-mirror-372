.. _draft_runs:

Draft Runs
==========
|
A draft run is the execution of a draft pipeline. Use draft runs for development purposes only.
The SDK enables you to interact with draft runs on the StreamSets Platform including starting a draft run, stopping a draft run, deleting a draft run, retrieving a draft run.
For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/DraftRuns/DraftRuns_title.html>`_
for draft runs.

.. note::
    A draft run can only run for a pipeline in draft mode.


Starting a Draft Run
~~~~~~~~~~~~~~~~~~~~
In the Platform UI, to start a draft run you have to visit the pipeline's canvas:

.. image:: ../_static/images/run/start_draftrun_ui.png

|

In the SDK to create a new :py:class:`streamsets.sdk.sch_models.DraftRuns` object or restart an existing :py:class:`streamsets.sdk.sch_models.DraftRuns` and add it to the Platform, first retrieve the :py:class:`streamsets.sdk.sch_models.Pipeline` object that you wish to create the draft run for.
Next pass that object to the :py:meth:`streamsets.sdk.ControlHub.start_draft_run`:

.. code-block:: python

    pipeline = sch.pipelines.get(name='Test Pipeline')
    sch.start_draft_run(pipeline=pipeline)

Retrieving an Existing Draft Run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In the Platform UI, a list of draft runs can be found and further filtered:

.. image:: ../_static/images/run/draftrun_ui.png

|

The equivalent steps in the SDK to retrieve, you can reference the :py:attr:`streamsets.sdk.ControlHub.draft_runs` attribute of your :py:class:`streamsets.sdk.ControlHub` instance.
You can also further filter and refine the Draft Runs returned based on attributes including ``job_name``, ``job_status``, and  ``job_id``:

.. code-block:: python

    # Returns a list of all draft run instances in 'INACTIVE' status
    sch.draft_runs.get_all(job_status='INACTIVE')
    # Retrieve a particular draft run's based on name
    draft_run = sch.draft_runs.get(job_name='job name')
    # Returns a single draft run instance that matches the supplied ID
    sch.draft_runs.get(id='acd9dea6-ffcd-4ae0-86e2-bef38c000304:9e1e3faa-ca28-4c05-9edb-3b18aaba4604')

Stopping a Draft Run
~~~~~~~~~~~~~~~~~~~~
When a draft run has served it's purpose but may need to be restarted later, you can stop the draft run.
In the Platform UI, stopping a draft run can be done as shown:

.. image:: ../_static/images/run/stop_draftrun_ui.png

|

The SDK equivalent of stopping a draft run requires first retrieving the :py:class:`streamsets.sdk.sch_models.DraftRun` object, then passing that object to the :py:meth:`streamsets.sdk.ControlHub.stop_draft_run` method:

.. code-block:: python

    # Get draft run instance to stop
    draft_run = sch.draft_runs.get(job_name='job name')
    sch.stop_draft_run(draft_run)

Deleting a Draft Run
~~~~~~~~~~~~~~~~~~~~

When a draft run has served it's purpose, and is no longer necessary you can delete the draft run.
Deleting a draft run in the UI can be done similarly to stopping:

.. image:: ../_static/images/run/delete_draftrun_ui.png

|

To delete a draft run in the SDK first retrieve the :py:class:`streamsets.sdk.sch_models.DraftRun` object next pass that object to the :py:meth:`streamsets.sdk.ControlHub.delete_draft_run` method:

.. code-block:: python

    # Get draft run instance to delete
    draft_run = sch.draft_runs.get(job_name='job name')
    sch.delete_draft_run(draft_run)

Snapshots
~~~~~~~~~
Once a snapshot is captured, it’s possible to inspect what data was captured.

In the UI snapshots can be accessed from the pipeline canvas once the draft run is started as shown below:

.. image:: ../_static/images/run/snapshots_ui.png

|

Retrieving an Existing Snapshot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To access snapshots for a draft run, reference the :py:attr:`streamsets.sdk.sch_models.DraftRun.snapshots` attribute of a :py:class:`streamsets.sdk.sch_models.DraftRun` instance.
This will return a :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Snapshot` objects that are in chronological order:

.. code-block:: python

    draft_run = sch.draftRuns.get(job_name='job name')
    # Get all snapshots belonging to that draft run
    snapshots = draft_run.snapshots
    # Get a specific snapshot
    snapshots = draft_run.snapshot.get(name="Snapshot3")

Capturing a Snapshot
~~~~~~~~~~~~~~~~~~~~~

To generate a snapshot for an existing draft run reference the :py:meth:`streamsets.sdk.sch_models.DraftRun.capture_snapshot`, you could use the following steps:

.. code-block:: python

    draft_run = sch.draftRuns.get(job_name='job name')
    draft_run.capture_snapshot()

Deleting a Snapshot
~~~~~~~~~~~~~~~~~~~

If you've successfully generated a snapshot for a pipeline and no longer need to retain it, it can be deleted using the :py:meth:`streamsets.sdk.sch_models.DraftRun.remove_snapshot` method.
The method expects to receive a :py:class:`streamsets.sdk.sch_models.DraftRun` instance as an argument:

.. code-block:: python

    draft_run = sch.draftRuns.get(job_name='job name')
    snapshot = draft_run.snapshots.get(name='snapshot_name')
    draft_run.remove_snapshot(snapshot)

Logs
~~~~

Retrieving logs
~~~~~~~~~~~~~~~
In the UI, you get view logs belonging to a draft run from the pipeline canvas:

.. image:: ../_static/images/run/logs_ui.png

|

In the SDK to view logs belonging to a draft run reference the :py:meth:`streamsets.sdk.sch_models.DraftRun.get_logs`, in return you get a :py:obj:`list` of :py:obj:`dict` instances, each a log line:

.. code-block:: python

    draft_run = sch.draftRuns.get(job_name='job name')
    logs = draft_run.get_logs()

Bringing It All Together
------------------------

The complete scripts from this section can be found below.

.. code-block:: python

    # Start a draft run
    pipeline = sch.pipelines.get(name='Test Pipeline')
    sch.start_draft_run(pipeline=pipeline)

    # Retrieve a particular draft run's based on name
    draft_run = sch.draft_runs.get(job_name='Draft Run for Test Pipeline')
    # Take Snapshot of draft run
    draft_run.capture_snapshot()
    # Get Snapshot
    snapshot = draft_run.snapshots.get(name='Snapshot1')
    # Remove snapshot
    draft_run.remove_snapshot(snapshot)
    # Get snapshot logs
    draft_run.get_logs()
    # Stop draft run instance
    sch.stop_draft_run(draft_run)
    # Delete Draft Run
    sch.delete_draft_run(draft_run)
