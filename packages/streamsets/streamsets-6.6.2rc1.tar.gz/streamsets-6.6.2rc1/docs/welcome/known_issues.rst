Known Issues
============
|

Please make note of the following known issues:

* Stages added to a pipeline via the SDK are not guaranteed to show up auto-arranged in the UI.
  This will be fixed in a future release of the SDK.
* If you wish to sort results by the last modified date when using the advanced search functionality in the SDK,
  the value given to the ``order_by`` parameter must be ``'MODIFIED_ON'`` as opposed to ``'LAST_MODIFIED_ON'``
  as typically seen with other usage. Please refer to the :ref:`StreamSets SDK Search Documentation <search_for_objects>`
  for further details
* Documentation sections need to be added.
* Slicing of ControlHub.pipelines returns inconsistent results

