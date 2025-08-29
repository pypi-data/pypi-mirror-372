Interacting with Pipeline Snapshots
===================================

Capturing a Snapshot
~~~~~~~~~~~~~~~~~~~~~

To generate a snapshot for an existing pipeline, you could use the following steps:

.. code-block:: python

    # Connect to a DataCollector instance and set the pipeline you wish to generate a snapshot for
    sdc = DataCollector("https://localhost:18630")
    pipeline = sdc.pipelines.get(id='testpipel1c35d2ff-5e49-4f99-ba56-00051fd7845f')

    # Capture the snapshot
    snapshot = sdc.capture_snapshot(pipeline).snapshot
    snapshot

**Output:**

.. code-block:: python

    <Snapshot (name=New Snapshot, time_stamp=1616718217886, batch_number=1)>


Reading from a Snapshot
~~~~~~~~~~~~~~~~~~~~~~~

Once a snapshot is captured, it's possible to inspect what data was captured.

Let's assume the above pipeline consisted of a Dev Data Generator origin writing to a Trash destination, with the
origin generating datetime data.

To read output values from a stage, you would execute the following:

.. code-block:: python

    # Select the stage you're interested in reading the output values for. In this case, the Origin stage
    stage = pipeline.stages[0]

    # Read the field attribute from output[0], which is the first record captured for the stage specified
    field = snapshot[stage].output[0].field

which returns a dictionary of the output:

.. code-block:: json

    {'random_value': 2018-11-05 04:31:05.953000}

To check a specific field's value from the output record you've just retrieved, you can index it directly by providing
the name of the field:

.. code-block:: python

    field['random_value']

**Output:**

.. code-block:: python

    datetime.datetime(2018, 11, 5, 4, 31, 5, 953000)


Note that the field value is coerced into the appropriate type, but the underlying raw value is stored along with its
type.

.. code-block:: python

    field['random_value'].raw_value
    field['random_value'].type

**Output:**

.. code-block:: python

    # field['random_value'].raw_value
    1541392265953

    # field['random_value'].type
    'DATETIME'

Retrieving an existing Snapshot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perhaps you had generated a snapshot for the same pipeline previously, either via the DataCollector UI or Python SDK,
and now you'd like to retrieve it. The following would allow you to pick a snapshot based on a number of unique
attributes such as ``id``, ``name``, or ``time_stamp``:

.. code-block:: python

    snapshot = sdc.get_snapshots(pipeline).get(name='Earlier Snapshot')
    snapshot

    snapshot.id

**Output:**

.. code-block:: python

    # snapshot
    <Snapshot (name=Earlier Snapshot, time_stamp=1616716207032, batch_number=1)>

    # snapshot.id
    'snapshot1616718217454'

Deleting a Snapshot
~~~~~~~~~~~~~~~~~~~

If you've successfully generated a snapshot for a pipeline and no longer need to retain it, it can be deleted using the
:py:meth:`streamsets.sdk.DataCollector.delete_snapshot` method. The method expects to receive a
:py:class:`streamsets.sdk.sdc_models.Snapshot` instance as an argument, exactly like the one returned by the
:py:meth:`streamsets.sdk.DataCollector.get_snapshots` method used previously:

.. code-block:: python

    # Check the list of current snapshots for the pipeline
    sdc.get_snapshots(pipeline)

    # Get the snapshot object that corresponds to the snapshot you wish to delete
    snapshot = sdc.get_snapshots(pipeline).get(name='New Snapshot')
    snapshot

    sdc.delete_snapshot(snapshot)

    # The snapshot has been deleted
    sdc.get_snapshots(pipeline)

**Output:**

.. code-block:: python

    # sdc.get_snapshots(pipeline)
    [<Snapshot (name=New Snapshot, time_stamp=1617379142414, batch_number=1)>,
     <Snapshot (name=Earlier Snapshot, time_stamp=1617379338310, batch_number=1)>]

    # snapshot
    <Snapshot (name=New Snapshot, time_stamp=1617379142414, batch_number=1)>

    # sdc.delete_snapshot(snapshot)
    <streamsets.sdk.sdc_api.Command object at 0x7f02c29eac88>

    # sdc.get_snapshots(pipeline)
    [<Snapshot (name=Earlier Snapshot, time_stamp=1617379338310, batch_number=1)>]

