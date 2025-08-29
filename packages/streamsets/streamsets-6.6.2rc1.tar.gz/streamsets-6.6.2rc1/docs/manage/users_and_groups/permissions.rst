Permissions
===========
|
Permissions determine the level of access that users or groups have on certain objects. In the Platform SDK,
these are represented via :py:class:`streamsets.sdk.sch_models.ACL` definitions (ACLs), which contain a list of
:py:class:`streamsets.sdk.sch_models.Permission` instances for each subject. A :py:class:`streamsets.sdk.sch_models.Permission`
instance stores the actions a user can take on the object.

ACLs do not exist as standalone objects in the SDK - they will always be contained within an object like a Job,
Deployment, or Pipeline.

.. tip::
  Accessing the ACL definition is the same for all objects in the SDK, regardless of their type. While not all objects
  have an ACL, objects that do have ACL permissions will always have them stored under the ``acl`` attribute. Likewise,
  the ACL will always have the structure of one permission definition per subject.

Find out more on Permissions in the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/OrganizationSecurity/Permissions.html#concept_e5n_fgm_wy>`_.

Retrieving an Object's ACL Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the Platform UI, you can typically see the permissions assigned to an object by selecting the object and
clicking on the 'Share' button as seen below:

.. image:: ../../_static/images/manage/permissions/share_button.png

|
This will show you the 'Sharing Settings' for the object, a breakdown of the permissions set for individual users and
groups:

.. image:: ../../_static/images/manage/permissions/share_settings.png

|
To retrieve an object's :py:class:`streamsets.sdk.sch_models.ACL` definition in the SDK, you can reference the ``acl``
attribute of the object. For example, to retrieve the ACL permissions of a :py:class:`streamsets.sdk.sch_models.Topology`
instance the following steps can be taken:

.. code-block:: python

    topology = sch.topologies.get(topology_name='ACL test topology')

    # Show the ACL object for this Topology
    topology.acl

    # Show the specific permission definitions that are part of the ACL
    topology.acl.permissions

**Output:**

.. code-block:: python

    # topology.acl
    <ACL (resource_id=3a2c521b-074d-4bc4-a216-fd204bd63bed:791759af-e8b5-11eb-8015-e592a7dbb2d0, resource_type=TOPOLOGY)>

    # topology.acl.permissions
    [<Permission (resource_id=3a2c521b-074d-4bc4-a216-fd204bd63bed:791759af-e8b5-11eb-8015-e592a7dbb2d0, subject_type=USER, subject_id=71c0fe4b-e8b5-11eb-8015-a133d38af703@791759af-e8b5-11eb-8015-e592a7dbb2d0)>,
     <Permission (resource_id=3a2c521b-074d-4bc4-a216-fd204bd63bed:791759af-e8b5-11eb-8015-e592a7dbb2d0, subject_type=GROUP, subject_id=pipeline_operators@791759af-e8b5-11eb-8015-e592a7dbb2d0)>]

.. note::
  The ``subject_id`` format for an ACL permission varies based on whether it pertains to a user or group. A user's
  ``subject_id`` will be in the format ``user.id@organization.id``, while a group's ``subject_id`` will be in the format
  ``group.group_id``.


You can inspect an ACL definition's actions to see the level of access a particular user or group has to the resource:

.. code-block:: python

    # Get the permission definition for a specific subject, the 'pipeline operators' group in this case
    topology.acl.permissions.get(subject_id='pipeline_operators@791759af-e8b5-11eb-8015-e592a7dbb2d0').actions

**Output:**

.. code-block:: python

    ['READ', 'WRITE']

Executable objects, such as :py:class:`streamsets.sdk.sch_models.ReportDefinition` or :py:class:`streamsets.sdk.sch_models.Job`
instances, also have an ``'EXECUTE'`` action that indicates a user or group can execute the object in question, e.g.
running a job or generating a report definition.

.. code-block:: python

    job = sch.jobs.get(job_name='Job for ACL pipeline')

    # Get the permission definition for a specific subject
    permission = job.acl.permissions.get(subject_id='71c0fe4b-e8b5-11eb-8015-a133d38af703@791759af-e8b5-11eb-8015-e592a7dbb2d0')

    # Show the actions set for that permission definition (the actions the user/group can take)
    permission.actions

**Output:**

.. code-block:: python

    # permission.actions
    ['READ', 'WRITE', 'EXECUTE']

Adding or Updating ACL Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the UI, adding new ACL permissions to an object, or updating the existing permissions, can be done in the same
'Sharing Settings' used to view existing user permissions. You can select the users or groups to add and then
select the permissions, or modify the permissions of existing users:

.. image:: ../../_static/images/manage/permissions/add_new_permissions.png

Adding New ACL permissions to an Object
---------------------------------------

To create a new permission definition for a user or group on an object using the SDK, the
:py:class:`streamsets.sdk.sch_models.ACLPermissionBuilder` class is used. While it is possible to instantiate a new
:py:class:`streamsets.sdk.sch_models.ACLPermissionBuilder` instance directly, most users will want to utilize the
builder that is already included within the :py:class:`streamsets.sdk.sch_models.ACL` definition of an object.

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

    # Get the user and group we want to set the permissions for
    user = sch.users.get(email_address='kramer@streamsets.com')
    group = sch.groups.get(display_name='new-group')

    # Build the new permission definition for the subject_id (id), subject_type (user or group) and the
    # actions to allow for this subject.
    user_permission = acl.permission_builder.build(subject_id=user.id, subject_type='USER', actions=actions)
    group_permission = acl.permission_builder.build(subject_id=group.group_id, subject_type='GROUP', actions=actions)

    # Add the permission definition to the ACL
    acl.add_permission(user_permission)
    acl.add_permission(group_permission)

    # Show that the permission definition was correctly added to the ACL
    pipeline.acl.permissions.get(subject_id=user.id)
    pipeline.acl.permissions.get(subject_id=group.group_id)


**Output:**

.. code-block:: python

    # pipeline.acl.permissions.get(subject_id=user.id)
    <Permission (resource_id=b99b5d55-380d-45a5-b8f1-0c9345fb662f:791759af-e8b5-11eb-8015-e592a7dbb2d0, subject_type=USER, subject_id=aa172288-c804-11ec-ba8b-4930c98e80a9@791759af-e8b5-11eb-8015-e592a7dbb2d0)>

    # pipeline.acl.permissions.get(subject_id=group.group_id)
    <Permission (resource_id=b99b5d55-380d-45a5-b8f1-0c9345fb662f:791759af-e8b5-11eb-8015-e592a7dbb2d0, subject_type=GROUP, subject_id=new_group@791759af-e8b5-11eb-8015-e592a7dbb2d0)>

Updating Existing ACL Permissions on an Object
----------------------------------------------

Updating an existing permission definition for an object's ACL is similar to creating a new permission definition.
Rather than building a brand new permission definition, you modify an existing one in-place. Retrieve the object you
wish to modify the ACL permissions for, retrieve the specific permission definition you want to update, and modify
the actions as needed:

.. code-block:: python

    pipeline = sch.pipelines.get(name='ACL pipeline')

    # Retrieve the permission definition for the subject to be modified
    group = sch.groups.get(display_name='new-group')
    permission = pipeline.acl.permissions.get(subject_id=group.group_id)

    # Create a list of new actions that the permission definition will use
    updated_actions = ['READ']

    # Set the actions for the permission to the new 'updated_actions' list
    permission.actions = updated_actions

    # Show that the permission definition was correctly added to the ACL
    pipeline.acl.permissions.get(subject_id=group.group_id).actions

**Output:**

.. code-block:: python

    # pipeline.acl.permissions.get(subject_id=group.group_id).actions
    ['READ']

.. note::
  ``ACL Permissions`` are limited to following actions:
  ``["READ"], ["READ", "WRITE"], ["READ", "EXECUTE"], or ["READ", "WRITE", "EXECUTE"]``.
Removing ACL permissions on an object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Removing permissions for a user or group in the UI is also done from the 'Sharing Settings'. Simply locate the user
or group to delete permissions for, and select the 'Delete' button:

.. image:: ../../_static/images/manage/permissions/delete_permissions.png

|
To remove an existing permission definition, the :py:meth:`streamsets.sdk.sch_models.ACL.remove_permission` method
is used. You'll first need to retrieve the specific permission you wish to delete from the ACL, and then pass it into
the method:

.. code-block:: python

    pipeline = sch.pipelines.get(name='ACL pipeline')

    # Retrieve the permission definition for the subject to be removed
    permission = pipeline.acl.permissions.get(subject_id='aa172288-c804-11ec-ba8b-4930c98e80a9@791759af-e8b5-11eb-8015-e592a7dbb2d0')

    # Remove the permission definition from the ACL
    response = pipeline.acl.remove_permission(permission)

Changing ownership of an object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To change ownership of an object from the UI, the 'Sharing Settings' are used once again. You'll need to locate the user
to set as the owner (or add them to the permissions if they don't yet exist), and select the 'Change Owner' button:

.. image:: ../../_static/images/manage/permissions/change_owner.png

|
To find the ID of the current owner of an object from the SDK, you can reference the ``resource_owner``
attribute of the ACL:

.. code-block:: python

    job = sch.jobs.get(job_name='Job for ACL pipeline')

    # Show the ID of the resource_owner for this Job, defined in the ACL
    job.acl.resource_owner

**Output:**

.. code-block:: python

    # job.acl.resource_owner
    '71c0fe4b-e8b5-11eb-8015-a133d38af703@791759af-e8b5-11eb-8015-e592a7dbb2d0'

Changing ownership of an object is as simple as specifying a new resource owner in the ACL for the object. The resource
owner value should be a valid user from the organization, specified using the ID of the user. Continuing
on from the example above:

.. code-block:: python

    new_owner = sch.users.get(email_address='kramer@streamsets.com')
    job.acl.resource_owner = new_owner.id
