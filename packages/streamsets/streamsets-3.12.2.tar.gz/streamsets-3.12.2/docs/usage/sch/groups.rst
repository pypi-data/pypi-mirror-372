Groups
======
|
Like users, groups also exist within the scope of an organization within Control Hub. Groups encompass 1 or more users,
and help further filter and categorize users within an organization.

Creating a new Group
~~~~~~~~~~~~~~~~~~~~

You can create a new :py:class:`streamsets.sdk.sch_models.Group` instance within a Control Hub organization via the
:py:class:`streamsets.sdk.sch_models.GroupBuilder` class. Use the :py:meth:`streamsets.sdk.ControlHub.get_group_builder`
method to instantiate the builder object:

.. code-block:: python

    group_builder = sch.get_group_builder()
    group = group_builder.build(id='test@admin', display_name='Test Group')
    group.users = ['admin@admin']
    sch.add_group(group)

Retrieving existing groups
~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieving existing groups from a Control Hub instance is as simple as asking for the ``groups`` attribute from the
:py:class:`streamsets.sdk.ControlHub` instance. You can further filter the available groups by specifying items
like ``id`` and ``display_name``:

.. code-block:: python

    # Get all groups belonging to current organization
    sch.groups

    # Get a particular group
    group = sch.groups.get(id='test@admin')
    group

    # Validate the users that are members of this group
    group.users

**Output:**

.. code-block:: python

    # sch.groups
    [<Group (id=all@admin, display_name=all)>,
     <Group (id=test@admin, display_name=Test Group)>]

    # group
    <Group (id=test@admin, display_name=Test Group)>

    # group.users
    ['test@admin', 'johnsmith@admin', 'janedoe@admin']

Updating an existing Group
~~~~~~~~~~~~~~~~~~~~~~~~~~

The SDK also allows for updating existing groups within an organization. Simply retrieve the group to be modified from
Control Hub, make the desired changes (such as adding a new user, or removing a role from the group), and then pass
the :py:class:`streamsets.sdk.sch_models.Group` instance to the :py:meth:`streamsets.sdk.ControlHub.update_group`
method:

.. code-block:: python

    group = sch.groups.get(display_name='Test Group')
    group.users.append('test@admin')
    group.roles.append('Data SLA User')
    group.roles.remove('Data SLA Editor')
    sch.update_group(group)

Deleting existing Groups
~~~~~~~~~~~~~~~~~~~~~~~~

Deleting existing groups from an organization is also done in a similar fashion. Simply retrieve the group(s) to be
deleted from Control Hub, and then pass the :py:class:`streamsets.sdk.sch_models.Group` instance(s) to the
:py:meth:`streamsets.sdk.ControlHub.delete_group` method:

.. code-block:: python

    # Delete a single group
    group = sch.groups.get(display_name='Test Group')
    sch.delete_group(group)

    # Delete multiple groups
    groups = sch.groups.get_all(display_name='Test Group')
    sch.delete_group(*groups)

