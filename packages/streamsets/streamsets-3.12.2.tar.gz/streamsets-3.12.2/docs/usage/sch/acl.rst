ACL Permissions
===============
|

Permissions determine the access level that users and groups have on objects. These are represented via :py:class:`streamsets.sdk.sch_models.ACL`
definitions (ACLs), which contain a list of :py:class:`streamsets.sdk.sch_models.Permission` instances for each subject.
A :py:class:`streamsets.sdk.sch_models.Permission` instance stores the actions a user can take on the object.

ACL permissions exist for numerous objects in Control Hub, including Execution Engines, Pipelines and Fragments, Jobs,
Provisioning Agents and Deployments, Topologies, Connections, Reports, Scheduled Tasks, and Subscriptions.

.. tip::
  Accessing the ACL definition is the same for all objects in the SDK, regardless of their type. While not all objects
  have an ACL, objects that do have ACL permissions will always have them stored under the ``acl`` attribute. Likewise,
  the ACL will always have the same structure of one permission definition per subject.

Find out more on Permissions in the `Control Hub Documentation <https://docs.streamsets.com/portal/#controlhub/latest/help/controlhub/UserGuide/OrganizationSecurity/Permissions.html#concept_e5n_fgm_wy>`_.

Retrieving an object's ACL permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve an object's :py:class:`streamsets.sdk.sch_models.ACL` definition, you can reference the ``acl`` attribute
of the object. For example, to retrieve the ACL permissions of a :py:class:`streamsets.sdk.sch_models.Topology` instance
the following steps can be taken:

.. code-block:: python

    topology = sch.topologies.get(topology_name='ACL test topology')

    # Show the ACL object for this Topology
    topology.acl

    # Show the specific permission definitions that are part of the ACL
    topology.acl.permissions

**Output:**

.. code-block:: python

    # topology.acl
    <ACL (resource_id=fe8f5ead-bee0-475f-b3b7-7875a89a6f0c:admin, resource_type=TOPOLOGY)>

    # topology.acl.permissions
    [<Permission (resource_id=fe8f5ead-bee0-475f-b3b7-7875a89a6f0c:admin, subject_type=USER, subject_id=admin@admin)>,
     <Permission (resource_id=fe8f5ead-bee0-475f-b3b7-7875a89a6f0c:admin, subject_type=USER, subject_id=user@admin)>,
     <Permission (resource_id=fe8f5ead-bee0-475f-b3b7-7875a89a6f0c:admin, subject_type=GROUP, subject_id=admin_group@admin)>]

|

You can inspect an individual ACL definition's actions to see the level of access a particular user or group has to
the resource:

.. code-block:: python

    # Get the permission definition for a specific subject, 'admin@admin' in this case
    permission = topology.acl.permissions.get(subject_id='admin@admin')

    # Show the actions that are set for that permission definition (the actions the user/group can take)
    permission.actions

**Output:**

.. code-block:: python

    ['READ', 'WRITE']

|

Executable objects, such as :py:class:`streamsets.sdk.sch_models.ReportDefinition` or :py:class:`streamsets.sdk.sch_models.Job`
instances, also have an ``'EXECUTE'`` action that indicates a user or group can execute the object in question, e.g.
running a job or generating a report definition.

.. code-block:: python

    job = sch.jobs.get(name='Job for ACL pipeline')

    # Get the permission definition for a specific subject, 'user@admin' in this case
    permission = job.acl.permissions.get(subject_id='user@admin')

    # Show the actions set for that permission definition (the actions the user/group can take)
    permission.actions

**Output:**

.. code-block:: python

    ['READ', 'WRITE', 'EXECUTE']

Adding new ACL permissions to an object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new permission definition for a user or group on an object, the :py:class:`streamsets.sdk.sch_models.ACLPermissionBuilder`
class is used. While it is possible to instantiate a new :py:class:`streamsets.sdk.sch_models.ACLPermissionBuilder`
instance directly, most users will want to utilize the builder that is already included within the :py:class:`streamsets.sdk.sch_models.ACL`
definition of an object.

The permission builder can be accessed directly via the :py:attr:`streamsets.sdk.sch_models.ACL.permission_builder`
attribute. It requires a subject_id, subject_type, and list of actions in order to build a permission definition. Once
the permission definition has been built, pass the permission definition to the :py:meth:`streamsets.sdk.sch_models.ACL.add_permission`
method to add it to the object that owns the ACL:

.. code-block:: python

    pipeline = sch.pipelines.get(name='ACL pipeline')

    # Retrieve the ACL definition of the pipeline
    acl = pipeline.acl

    # Create a list of actions to add for the new permission definition
    actions = ['READ', 'WRITE']

    # Build the new permission definition for the subject_id (username), subject_type (user or group) and the
    # actions to allow for this subject.
    permission = acl.permission_builder.build(subject_id='user@admin', subject_type='USER', actions=actions)

    # Add the permission definition to the ACL
    acl.add_permission(permission)

    # Show that the permission definition was correctly added to the ACL
    pipeline = sch.pipelines.get(name='ACL pipeline')
    pipeline.acl.permissions.get(subject_id='user@admin').actions

**Output:**

.. code-block:: python

    ['READ', 'WRITE']

Updating existing ACL permissions on an object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updating an existing permission definition for an object's ACL is similar to creating a new permission definition, but
rather than building a brand new permission definition, you simply modify an existing one in-place. Retrieve the object
you wish to modify the ACL permissions for, retrieve the specific permission definition you want to update, and modify
the actions as needed:

.. code-block:: python

    pipeline = sch.pipelines.get(name='ACL pipeline')

    # Retrieve the permission definition for the subject to be modified
    permission = pipeline.acl.permissions.get(subject_id='user@admin')

    # Create a list of new actions that the permission definition will use
    updated_actions = ['READ']

    # Set the actions for the permission to the new 'updated_actions' list
    permission.actions = updated_actions

    # Show that the permission definition was correctly added to the ACL
    pipeline = sch.pipelines.get(name='ACL pipeline')
    pipeline.acl.permissions.get(subject_id='user@admin').actions

**Output:**

.. code-block:: python

    ['READ']

Removing ACL permissions on an object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To remove an existing permission definition, the :py:meth:`streamset.sdk.sch_models.ACL.remove_permission` method
is used. You'll first need to retrieve the specific permission you wish to delete from the ACL, and then pass it into
the method:

.. code-block:: python

    report_definition = sch.report_definitions.get(name='ACL test report')

    # Retrieve the permission definition for the subject to be removed
    permission = report_definition.acl.permissions.get(subject_id='user2@admin')

    # Remove the permission definition from the ACL
    report_definition.acl.remove_permission(permission)

Changing ownership of an object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An object's ACL permissions also dictate who the owner of the object is. To inspect the owner, you can reference the
``resource_owner`` attribute of the ACL:

.. code-block:: python

    job = sch.jobs.get(job_name='Job for ACL test')

    # Show the ACL object for this Job
    job.acl

    # Show the resource_owner for this Job, defined in the ACL
    job.acl.resource_owner

**Output:**

.. code-block:: python

    # job.acl
    <ACL (resource_id=890cccd2-ed8c-4416-88f7-d38a54844ab9:admin, resource_type=JOB)>

    # job.acl.resource_owner
    'admin@admin'

|

Changing ownership of an object is as simple as specifying a new resource owner in the ACL for the object. The resource
owner value should be a valid user from the organization, specified in the ``'user@organization'`` format. Continuing
on from the sample above:

.. code-block:: python

    job.acl.resource_owner = 'user@admin'
