Connections
===========
|
A connection defines the information required to connect to an external system. Rather than providing these details
repeatedly in every pipeline that accesses the same system, a connection can be created to store those details
centrally and reused across multiple pipelines.

Creating a new connection
~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new connection and add it to Control Hub, use the :py:class:`streamsets.sdk.sch_models.ConnectionBuilder`
class. Use the :py:meth:`streamsets.sdk.ControlHub.get_connection_builder` method to instantiate the builder
object.

The :py:class:`streamsets.sdk.sch_models.Connection` object can then be passed to the :py:meth:`streamsets.sdk.ControlHub.add_connection`
method to be published in Control Hub:

.. code-block:: python

    connection_builder = sch.get_connection_builder()
    data_collector = sch.data_collectors.get(url='http://localhost:18630')
    connection = connection_builder.build(title='s3 connection dev',
                                          connection_type='AWS_S3',
                                          authoring_data_collector=data_collector)
    connection.connection_definition.configuration['awsConfig.awsAccessKeyId'] = 123
    connection.connection_definition.configuration['awsConfig.awsSecretAccessKey'] = 456
    sch.add_connection(connection)

Please refer to the `Control Hub documentation <https://docs.streamsets.com/portal/#controlhub/latest/help/controlhub/UserGuide/Connections/Connections_title.html>`_
for the available connection types and various configurations.

Retrieving connections
~~~~~~~~~~~~~~~~~~~~~~

Retrieving connections from Control Hub is a simple task. You can reference :py:attr:`streamsets.sdk.ControlHub.connections`
to retrieve all existing connections. Likewise, you can further filter the available connections on attributes like ``name``, ``connection_type`` and ``id``:

.. code-block:: python

    sch.connections

    # Retrieve all connections with JDBC type
    sch.connections.get_all(connection_type='STREAMSETS_JDBC')

**Output:**

.. code-block:: python

    # sch.connections
    [<Connection (id='25dc5a92-a01c-4fef-979c-824000053396:admin',
     name='s3 connection dev',
     connection_type='STREAMSETS_AWS_S3')>]

    # sch.connections.get_all(connection_type='STREAMSETS_JDBC')
    [<Connection (id=6b8d75e2-7595-48ac-a6d2-cade5cafcc42:admin, name=Test, connection_type=STREAMSETS_JDBC)>,
     <Connection (id=3afe2ce6-db7d-4c05-a6b0-1ab2b667ea67:admin, name=test mysql connection, connection_type=STREAMSETS_JDBC)>]

Updating a connection
~~~~~~~~~~~~~~~~~~~~~

To update a connection, first retrieve the :py:class:`streamsets.sdk.sch_models.Connection` object you wish
to update. You can make modifications to attributes like the ``name`` or various connection-specific configurations.
Once you've made the desired changes, use the :py:meth:`streamsets.sdk.ControlHub.update_connection` method to push the
updated connection to Control Hub:

.. code-block:: python

    connection = sch.connections.get(name='s3 connection dev')
    connection.connection_definition.configuration['awsConfig.awsAccessKeyId'] = 234
    connection.connection_definition.configuration['awsConfig.awsSecretAccessKey'] = 567
    connection.name = 's3 connection prod'
    sch.update_connection(connection)

Deleting a connection
~~~~~~~~~~~~~~~~~~~~~

To delete a connection, first retrieve the :py:class:`streamsets.sdk.sch_models.Connection` object you wish
to delete, and then pass it to the :py:meth:`streamsets.sdk.ControlHub.delete_connection` method:

.. code-block:: python

    connection = sch.connections.get(name='s3 connection prod')
    sch.delete_connection(connection)

Using a connection inside a pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After building a connection and adding it to Control Hub, the connection is available for use within a pipeline. To add
a connection to a pipeline, the steps are almost identical to building a normal pipeline - retrieve a
:py:class:`streamsets.sdk.sch_models.DataCollector` instance to use as an Authoring Data Collector (if desired),
retrieve the :py:class:`streamsets.sdk.sch_models.Connection` instance to add to the pipeline, instantiate a
:py:class:`streamsets.sdk.sch_models.PipelineBuilder` object to build the pipeline with, add and configure some stages
for the pipeline, and then finally add the connection and publish the pipeline:

.. code-block:: python

    # Retrieve a Data Collector instance to use as the Authoring Data Collector (optional)
    data_collector = sch.data_collectors.get(url='http://localhost:18630')

    # Retrieve the connection to be used inside the pipeline
    connection = sch.connections.get(name='s3 connection prod')

    # Create the pipeline builder instance as you would with any other pipeline
    pipeline_builder = sch.get_pipeline_builder(data_collector)

    # Add stages to the pipeline, set some attributes in the stages, and then connect the stages together
    dev_raw_data_source = pipeline_builder.add_stage('Dev Raw Data Source')
    dev_raw_data_source.stop_after_first_batch = True
    amazon_s3_destination = pipeline_builder.add_stage('Amazon S3', type='destination')
    amazon_s3_destination.set_attributes(bucket='bucket-name', data_format='JSON')
    dev_raw_data_source >> amazon_s3_destination

    # Set the destination stage (AWS S3 in this example) to use the connection retrieved earlier
    amazon_s3_destination.use_connection(connection)

    # Build and publish the pipeline
    pipeline = pipeline_builder.build('Dev to S3')
    sch.publish_pipeline(pipeline)

Verifying a connection
~~~~~~~~~~~~~~~~~~~~~~

Once a connection is built and added to Control Hub, it can be further tested for connectivity to verify that it's
successfully connecting. To verify a connection, retrieve the :py:class:`streamsets.sdk.sch_models.Connection`
instance you want to validate and then use the :py:meth:`streamsets.sdk.ControlHub.verify_connection` method to return
the results of the verification.

If any issues arise during the connection's verification, you can introspect on the :py:attr:`streamsets.sdk.sch_models.ConnectionVerificationResult.issue_count`
and :py:attr:`streamsets.sdk.sch_models.ConnectionVerificationResult.issue_message` to identify the issue:

.. code-block:: python

    # Retrieve the connection to be verified
    connection = sch.connections.get(name='s3 connection prod')

    # Run the verification, and then check the results (successful case)
    verification_result = sch.verify_connection(connection)
    verification_result

    connection = sch.connections.get(name='s3 connection invalid')

    # Run the verification, and then check the results (failure case)
    verification_result = sch.verify_connection(connection)
    verification_result
    verification_result.issue_count
    verification_result.issue_message

**Output:**

.. code-block:: python

    # verification_result
    <ConnectionVerificationResult (status=VALID)>

    #verification_result
    <ConnectionVerificationResult (status=INVALID)>

    # verification_result.issue_count
    1

    # verification_result.issue_message
    'S3_SPOOLDIR_20 - Cannot connect to Amazon S3, reason : com.amazonaws.services.s3.model.AmazonS3Exception:
    The request signature we calculated does not match the signature you provided. Check your key and signing method.'

Get pipelines using a connection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve all pipelines using a specific connection, first retrieve the :py:class:`streamsets.sdk.sch_models.Connection`
object you'd like to check against and then reference the :py:attr:`streamsets.sdk.sch_models.Connection.pipeline_commits`
attribute to determine which pipelines are currently using the connection:

.. code-block:: python

    # Get the connection to check the usage of
    connection = sch.connections.get(name='s3 connection prod')

    # Check the pipeline commits that currently use this connection
    connection.pipeline_commits

    # Introspect a little further and identify the pipeline details for the first (and only) pipeline commit above
    connection.pipeline_commits[0].pipeline

**Output:**

.. code-block:: python

    #connection.pipeline_commits
    [<PipelineCommit (commit_id=db1e3b87-1499-44ef-93b8-e4e045318c48:admin, version=1, commit_message=None)>]

    # connection.pipeline_commits[0].pipeline
    <Pipeline (pipeline_id=5462626e-0243-48dd-8c07-c6787a813e37:admin,
     commit_id=db1e3b87-1499-44ef-93b8-e4e045318c48:admin, name=s3, version=1)>

Retrieving ACL permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~

Connections can also have ACL permissions set on them to restrict access. To retrieve existing ACL permissions set on a
given connection, reference the :py:attr:`streamsets.sdk.sch_models.Connection.acl.permissions` attribute for the
connection object you wish to check:

.. code-block:: python

    connection = sch.connections.get(name='s3 connection prod')

    # Check which ACL resource is set for this connection
    connection.acl
    <ACL (resource_id=cadd8eaa-85f4-48d0-a1a0-ff77a63584cc:admin, resource_type=CONNECTION)>

    # Check the specific permissions set by this connection's ACL resource
    connection.acl.permissions

**Output:**

.. code-block:: python

    # connection.acl
    <ACL (resource_id=cadd8eaa-85f4-48d0-a1a0-ff77a63584cc:admin, resource_type=CONNECTION)>

    # connection.acl.permissions
    [<Permission (resource_id=cadd8eaa-85f4-48d0-a1a0-ff77a63584cc:admin, subject_type=USER, subject_id=admin@admin)>]

Adding new permissions
~~~~~~~~~~~~~~~~~~~~~~

Adding new permissions to a connection via the SDK is similar to permission management in other SDK classes. Retrieve
the :py:class:`streamsets.sdk.sch_models.Connection` object you wish to modify permissions for, store the current ACL
permissions for the connection, generate a new set of permissions using the :py:meth:`streamsets.sdk.sch_models.ACLPermissionBuilder.build`
method, and then add them back to the connection using the :py:meth:`streamsets.sdk.sch_models.ACL.add_permission`
method:

.. code-block:: python

    # Get the connection object to be modified
    connection = sch.connections.get(name='s3 connection prod')

    # Store the ACL permissions of the connection object
    acl = connection.acl

    # Generate a new list that stores the specific permissions to be added later
    actions = ['READ', 'WRITE']

    # Build the new permissions by supplying a subject_id (username), subject_type (user or group) and the
    # permissions to be set (the list created above)
    permission = acl.permission_builder.build(subject_id='testuser@testorg', subject_type='USER', actions=actions)

    # Add the permissions to the ACL object stored for the connection earlier
    acl.add_permission(permission)

    # Double check that the permissions were correctly added
    connection = sch.connections.get(name='s3 connection prod')
    connection.acl.permissions.get(subject_id='testuser@testorg')

**Output:**

.. code-block:: python

    <Permission (resource_id=cadd8eaa-85f4-48d0-a1a0-ff77a63584cc:admin, subject_type=USER, subject_id=testuser@testorg)>

Updating existing permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updating existing permissions for a connection is a similar exercise to creating new permissions - rather than building
a brand new permission set, you simply update an existing one in-place. Retrieve the :py:class:`streamsets.sdk.sch_models.Connection`
object you wish to modify permissions for, retrieve the specific permissions you wish to update, and then modify the
permissions as needed:

.. code-block:: python

    # Get the connection object to be modified
    connection = sch.connections.get(name='s3 connection prod')

    # Get the specific permissions to be modified
    permission = connection.acl.permissions.get(subject_id='testuser@testorg')

    # Create a list of new permissions to be set
    updated_actions = ['READ']

    # Set the actions of the permission, retrieved earlier, to be the list of new permissions
    permission.actions = updated_actions

    # Double check that the permissions were correctly updated
    connection = sch.connections.get(name='s3 connection prod')
    connection.acl.permissions.get(subject_id=permission.subject_id).actions

**Output:**

.. code-block:: python

    ['READ']

Removing existing permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To remove existing permissions on a connection object, use the :py:class:`streamsets.sdk.sch_models.Connection` object's
:py:meth:`streamsets.sdk.sch_models.ACL.remove_permission` method:

.. code-block:: python

    # Get the connection object to be modified
    connection = sch.connections.get(name='s3 connection prod')

    # Retrieve the specific permission to be removed
    permission = connection.acl.permissions.get(subject_id='testuser@testorg')

    # Remove the permission
    connection.acl.remove_permission(permission)

