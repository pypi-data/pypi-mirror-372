.. _saql_saved_searches:

Saved Searches
=================

After defining search conditions, a search can be saved for later use allowing you to quickly filter your Pipelines, Fragments, Jobs, Job Templates & Draft Runs without having to define a new search query.
More information on SAQL Saved Searches can be found in the `StreamSets Platform Documentation  <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/Search/Searching_title.html#concept_sr1_lzw_kwb>`_.

Retrieving Saved Searches
~~~~~~~~~~~~~~~~~~~~~~~~~

In the UI, you can retrieve your Saved searches by selecting 'Saved Searches' from the additional options menu:

.. image:: ../_static/images/search/SAQL_Saved_Searches.png

|
Retrieving saved searches using the SDK can be done by referencing the following properties of a :py:class:`streamsets.sdk.ControlHub` instance:

#. Saved searches pertaining to Pipelines can be accessed via the :py:attr:`streamsets.sdk.ControlHub.saql_saved_searches_pipeline` attribute
#. Saved searches pertaining to Fragments can be accessed via the :py:attr:`streamsets.sdk.ControlHub.saql_saved_searches_fragment` attribute
#. Saved searches pertaining to Job Instances can be accessed via the :py:attr:`streamsets.sdk.ControlHub.saql_saved_searches_job_instance` attribute
#. Saved searches pertaining to Job Templates can be accessed via the :py:attr:`streamsets.sdk.ControlHub.saql_saved_searches_job_template` attribute
#. Saved searches pertaining to Draft Runs can be accessed via the :py:attr:`streamsets.sdk.ControlHub.saql_saved_searches_draft_run` attribute

If you wanted to retrieve and store all of the various saved searches for each supported object, you could do so using the following:

.. code-block:: python

    sch.saql_saved_searches_pipeline
    sch.saql_saved_searches_fragment
    sch.saql_saved_searches_job_instance
    sch.saql_saved_searches_job_template
    sch.saql_saved_searches_draft_run

You can also filter the saved searches by specifying attributes like ``name``, ``creator`` or ``type``.
For example, retrieving all saved searches pertaining to Job Templates that are marked as a favorite would look like the following:

.. code-block:: python

    job_template_favorite_searches = sch.saql_saved_searches_job_template.get_all(favorite=True)


Creating a Saved Search
~~~~~~~~~~~~~~~~~~~~~~~
In the UI, creating a saved search can be done by providing values for ‘Query Name’, ‘Query Operator’ and ‘Query Value’ and selecting search as seen below.

.. image:: ../_static/images/search/SAQL_Query_Builder.png

|
You can then save the search by selecting 'Save this Search' from the additional options menu:

.. image:: ../_static/images/search/SAQL_Save_Search.png

|
In the SDK, we mirror this functionality by having users build a query using the :py:class:`streamsets.sdk.sch_models.SAQLSearchBuilder` class.
You can retrieve an instance of this class by using the :py:meth:`streamsets.sdk.ControlHub.get_saql_search_builder` method with the ``saql_search_type`` and ``mode`` parameters:

.. code-block:: python

    saql_search_builder = sch.get_saql_search_builder(saql_search_type='PIPELINE', mode='BASIC')


Once you’ve retrieved your :py:class:`streamsets.sdk.sch_models.SAQLSearchBuilder` instance, creating a search is as simple as calling the :py:meth:`streamsets.sdk.sch_models.SAQLSearchBuilder.add_filter` method and providing values for the ``property_name``, ``property_operator``, ``property_value``, and ``property_condition_combiner`` parameters.

To use the SDK to recreate the query from the UI example above, you could do the following:

.. code-block:: python

    saql_search_builder.add_filter(property_name='name', property_operator='contains', property_value='Test Name', property_condition_combiner='AND')

Once you've built the query, you can build and save the search.
This can be done by calling the :py:meth:`streamsets.sdk.sch_models.SAQLSearchBuilder.build` method and providing a value for the ``name`` parameter. This will return a :py:class:`streamsets.sdk.sch_models.SAQLSearch` instance.

.. code-block:: python

    saql_search_object = saql_search_builder.build(name='TEST BASIC QUERY')

Alternatively, if you wanted to create the saql_search_object directly using a query string, you can create a :py:class:`streamsets.sdk.sch_models.SAQLSearchBuilder` instance with with ``mode`` set to 'ADVANCED', then you could inject the query string into the ``query`` attribute of the :py:class:`streamsets.sdk.sch_models.SAQLSearch` instance and build it.

.. code-block:: python

    saql_search_builder = sch.get_saql_search_builder(saql_search_type='PIPELINE', mode='ADVANCED')
    saql_search_builder.query = "name == *pipeline2*"
    saql_search_object = saql_search_builder.build(name='TEST ADVANCED QUERY')

.. note::
    Currently, the only ``saql_search_type`` values that are supported are ``'PIPELINE'``, ``'FRAGMENT'``, ``'JOB_INSTANCE'``, ``'JOB_TEMPLATE'``, ``'JOB_DRAFT_RUN'``.

Finally, pass the newly-created :py:class:`streamsets.sdk.sch_models.SAQLSearch` instance to the :py:meth:`streamsets.sdk.ControlHub.save_saql_search` method to save the search on Control Hub:

.. code-block:: python

    sch.save_saql_search(saql_search_object)

Using a Saved Search
~~~~~~~~~~~~~~~~~~~~
As seen in the 'Creating a Saved Search' section, using a saved search in the UI on your Pipelines, Fragments, Jobs, Job Templates & Draft Runs entails creating your query and clicking on the search button.

In the SDK, using a saved search entails grabbing the saved search object and passing its query into either the :py:attr:`streamsets.sdk.ControlHub.pipelines` attribute or the :py:attr:`streamsets.sdk.ControlHub.jobs` attribute depending on the type of object you are searching against.

If you want to search against Jobs, Job Templates or Draft Runs, you would then use the :py:attr:`streamsets.sdk.ControlHub.jobs` attribute. Here's an an example of searching for all Job Instances which match a certain query:

.. code-block:: python

    job_instances_saql_search = sch.saql_saved_searches_job_instance.get(name='Job Instance Sample Query')
    sch.jobs.get_all(search=job_instances_saql_search.query)

If you want to search against Pipelines or Fragments, you would then use the :py:attr:`streamsets.sdk.ControlHub.pipelines` attribute. Here's an an example of searching for a Fragment which matches a certain query:

.. code-block:: python

    fragment_saql_search = sch.saql_saved_searches_fragment.get(name='Fragment Sample Query')
    sch.pipelines.get(search=fragment_saql_search.query)

Marking a Saved Search as a Favorite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In the UI, marking a search as a favorite entails going into your ‘Saved Searches’, finding the desired search and selecting the star icon:

.. image:: ../_static/images/search/SAQL_Mark_Favorite.png

|
To mark a search as a favorite in the SDK, retrieve the :py:class:`streamsets.sdk.sch_models.SAQLSearch` instance you wish to mark as a favorite and pass it to the :py:meth:`streamsets.sdk.ControlHub.mark_saql_search_as_favorite` method.
Similarly, to un-mark a search as a favorite, you would pass the :py:class:`streamsets.sdk.sch_models.SAQLSearch` instance you wish to un-mark into the :py:meth:`streamsets.sdk.ControlHub.mark_saql_search_as_favorite` method:

.. code-block:: python

    sch.mark_saql_search_as_favorite(saql_search_object)

To check if a :py:class:`streamsets.sdk.sch_models.SAQLSearch` instance is currently a favorite or not, reference the instance's ``favorite`` attribute which will return ``True`` or ``False``:

.. code-block:: python

    saql_search_object.favorite

Updating a Saved Search
~~~~~~~~~~~~~~~~~~~~~~~

In the UI, updating a search entails going into your ‘Saved Searches’, finding the desired search and selecting the pencil icon:

.. image:: ../_static/images/search/SAQL_Update.png

|
To update a :py:class:`streamsets.sdk.sch_models.SAQLSearch` instance, update an attribute like the instance's ``name`` and then pass the instance into the :py:meth:`streamsets.sdk.ControlHub.update_saql_search` method:

.. code-block:: python

    saql_search_object.name = 'new_name'
    sch.update_saql_search(saql_search_object)

.. note::
    Currently, only renaming SAQL Searches is supported.

Removing a saved search
~~~~~~~~~~~~~~~~~~~~~~~

In the UI, removing a search entails going into your ‘Saved Searches’, finding the desired search and selecting the Trash icon:

.. image:: ../_static/images/search/SAQL_Remove.png

|
To remove a :py:class:`streamsets.sdk.sch_models.SAQLSearch` instance, pass the instance into the :py:meth:`streamsets.sdk.ControlHub.remove_saql_search` method:

.. code-block:: python

    sch.remove_saql_search(saql_search_object)

Bringing It All Together
------------------------

The complete scripts from this section can be found below.
Commands that only served to verify some output from the example have been removed.

.. code-block:: python

    # Get saved searches
    sch.saql_saved_searches_pipeline
    sch.saql_saved_searches_fragment
    sch.saql_saved_searches_job_instance
    sch.saql_saved_searches_job_template
    sch.saql_saved_searches_draft_run
    job_template_favorite_searches = sch.saql_saved_searches_job_template.get_all(favorite=True)

    # create a builder object
    saql_search_builder = sch.get_saql_search_builder(saql_search_type='PIPELINE', mode='BASIC')

    # add filters to the query and create the saql_search_object
    saql_search_builder.add_filter(property_name='name', property_operator='contains', property_value='Test Name', property_condition_combiner='AND')
    saql_search_object = saql_search_builder.build(name='TEST BASIC QUERY')

    # add a query string directly to the builder and create the saql_search_object
    # saql_search_builder = sch.get_saql_search_builder(saql_search_type='PIPELINE', mode='ADVANCED')
    # saql_search_builder.query = "name == *pipeline2*"
    # saql_search_object = saql_search_builder.build(name='TEST ADVANCED QUERY')

    # save a search
    sch.save_saql_search(saql_search_object)

    # search for all job instances which match a certain query
    job_instances_saql_search = sch.saql_saved_searches_job_instance.get(name='Job Instance Sample Query')
    sch.jobs.get_all(search=job_instances_saql_search.query)

    # search for a fragment which matches a certain query
    fragment_saql_search = sch.saql_saved_searches_fragment.get(name='Fragment Sample Query')
    sch.pipelines.get(search=fragment_saql_search.query)

    # mark a search as a favorite
    sch.mark_saql_search_as_favorite(saql_search_object)

    # update a search
    saql_search_object.name = 'new_name'
    sch.update_saql_search(saql_search_object)

    # removing a search
    sch.remove_saql_search(saql_search_object)
