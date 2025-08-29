Connection Tags
===============
|
A Connection Tag identifies similar connections and allows you to easily search and filter connections.

Creating a connection with tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add a tag to a connection at creation time, simply include a ``tags`` argument in the
:py:meth:`streamsets.sdk.sch_models.ConnectionBuilder.build` method:

.. code-block:: python

    connection_builder = sch.get_connection_builder()
    data_collector = sch.data_collectors.get(url='http://localhost:18630')

    # Create a list to store the tags to add to the connection at creation time
    tags = ['test/dev', 'test']

    # Add the list of tags into the builder via `tags=tags`
    connection = connection_builder.build(title='s3 connection dev',
                                          connection_type='AWS_S3',
                                          authoring_data_collector=data_collector,
                                          tags=tags)
    connection.connection_definition.configuration['awsConfig.awsAccessKeyId'] = 123
    connection.connection_definition.configuration['awsConfig.awsSecretAccessKey'] = 456
    sch.add_connection(connection)

    # Double check that the tags were successfully added
    connection.tags

**Output:**

.. code-block:: python

    [<Tag (tag=test/dev)>,
     <Tag (tag=test)>]

Updating tags of an existing connection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To update the tags of an existing connection via the sdk, retrieve the :py:class:`streamsets.sdk.sch_models.Connection`
object you want to update and use its :py:meth:`streamsets.sdk.sch_models.Connection.add_tag` method to pass in the tags
you want to add. Finally, pass the modified connection to the :py:meth:`streamsets.sdk.ControlHub.update_connection`
method to push the changes to Control Hub:

.. code-block:: python

    connection = sch.connections.get(name='s3 connection dev')
    connection.add_tag('prod/dev', 'prod')
    sch.update_connection(connection)
    connection.tags

**Output:**

.. code-block:: python

    [<Tag (tag=test/dev)>,
     <Tag (tag=test)>,
     <Tag (tag=prod/dev)>,
     <Tag (tag=prod)>]

Removing existing tags for a connection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to adding tags for a connection, removing tags requires the same steps. Retrieve the :py:class:`streamsets.sdk.sch_models.Connection`
object you want to update and use its :py:meth:`streamsets.sdk.sch_models.Connection.remove_tag` method to specify the
the tags you wish to remove from the connection. Finally, pass the modified connection to the :py:meth:`streamsets.sdk.ControlHub.update_connection`
method to push the changes to Control Hub:

.. code-block:: python

    connection = sch.connections.get(name='s3 connection dev')
    connection.remove_tag('test', 'test/dev')
    sch.update_connection(connection)
    connection.tags

**Output:**

.. code-block:: python

    [<Tag (tag=prod/dev)>,
     <Tag (tag=prod)>]]

Retrieve all connection tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve all connection tags that exist in Control Hub for your organization, reference the :py:attr:`streamsets.sdk.ControlHub.connection_tags`
attribute for your Control Hub instance:

.. code-block:: python

   sch.connection_tags

**Output:**

.. code-block:: python

   [<Tag (tag=dev)>, <Tag (tag=prod)>]

Similarly if you wanted to retrieve all connections by a particular parent ID, you could use the ``parent_id`` attribute
to further filter the results:

.. code-block:: python

   sch.connection_tags.get_all(parent_id='prod:{}'.format(sch.organization))

**Output:**

.. code-block:: python

   [<Tag (tag=prod/data)>, <Tag (tag=prod/pipeline)>]

Connection audits
~~~~~~~~~~~~~~~~~

Changes to connections on Control Hub also have an audit trail that can be interacted with via the SDK.
To retrieve connection audits for last 30 days, you can reference the :py:attr:`streamsets.sdk.ControlHub.connection_audits`
attribute:

.. code-block:: python

    sch.connection_audits

**Output:**

.. code-block:: python

    [<ConnectionAudit (user_id=admin@admin,
                       connection_name=s3 connection prod,
                       audit_action=UPDATE,
                       audit_time=1601574060023)>,
     <ConnectionAudit (user_id=admin@admin,
                       connection_name=s3 connection prod,
                       audit_action=CREATE,
                       audit_time=1601574050166)>]

To retrieve connection audits for a specific time period, you'll still reference the :py:attr:`streamsets.sdk.ControlHub.connection_audits`
attribute but can filter the results further by providing a ``start_time`` and ``end_time``:

.. code-block:: python

    import datetime
    current_timestamp = datetime.datetime.now().timestamp() * 1000
    sch.connection_audits.get_all(start_time=0, end_time=current_timestamp)

**Output:**

.. code-block:: python

    [<ConnectionAudit (user_id=admin@admin,
                       connection_name=s3 connection prod,
                       audit_action=UPDATE,
                       audit_time=1601574060023)>,
     <ConnectionAudit (user_id=admin@admin,
                       connection_name=s3 connection prod,
                       audit_action=CREATE,
                       audit_time=1601574050166)>]

To retrieve connection audits for a specific connection, you will again reference the :py:attr:`streamsets.sdk.ControlHub.connection_audits`
attribute but will provide a specific :py:class:`streamsets.sdk.sch_models.Connection` object to filter the results by:

.. code-block:: python

    connection = sch.connections.get(name='s3 connection invalid')
    sch.connection_audits.get_all(connection=connection)

**Output:**

.. code-block:: python

    [<ConnectionAudit (user_id=admin@admin,
                       connection_name=s3 connection prod,
                       audit_action=UPDATE,
                       audit_time=1601574060023)>,
     <ConnectionAudit (user_id=admin@admin,
                       connection_name=s3 connection prod,
                       audit_action=CREATE,
                       audit_time=1601574050166)>]

To retrieve connection audits for a different organization, you'll need to be a system administrator for Control Hub.
You will still reference the :py:attr:`streamsets.sdk.ControlHub.connection_audits` attribute, but will specify the
``organization='org_name'`` for which you'd like to retrieve connection audits for:

.. code-block:: python

    sch.connection_audits.get_all(organization='test', start_time=0, end_time=current_timestamp)

**Output:**

.. code-block:: python

    [<ConnectionAudit (user_id=admin@test,
                       connection_name=s3 connection test,
                       audit_action=UPDATE,
                       audit_time=1601574060023)>,
     <ConnectionAudit (user_id=admin@test,
                       connection_name=s3 connection test,
                       audit_action=CREATE,
                       audit_time=1601574050166)>]
