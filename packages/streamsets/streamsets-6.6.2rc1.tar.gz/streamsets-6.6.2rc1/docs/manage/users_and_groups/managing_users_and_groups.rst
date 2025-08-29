Managing Users and Groups
=========================
|

The SDK allows you to manage users and groups for your organization including creating new groups, inviting users,
activating or deactivating existing users, and adding users to groups.

The SDK is designed to mirror the Platform UI. This section will show references and examples of how certain
actions are taken in the UI, followed the equivalent actions in the SDK.

Users
~~~~~

Retrieving Existing Users
-------------------------

In the UI of a Platform Organization, you can check the existing users as seen in the below screenshot:

.. image:: ../../_static/images/manage/users_and_groups/users_list.png

|
Existing users in your Platform organization are stored in the ``users`` attribute of the
:py:class:`streamsets.sdk.ControlHub` object you've instantiated. You can further filter the list of available users by
specifying items like ``id``, ``email_address``, or ``status``:

.. code-block:: python

    # Get all users belonging to current organization
    sch.users

    # Get a particular user
    sch.users.get(email_address='mitch@streamsets.com')

    # Get all currently deactivated users
    sch.users.get_all(status='DEACTIVATED')

**Output:**

.. code-block:: python

    # sch.users
    [<User (email_address=kramer@streamsets.com, display_name=, status=DEACTIVATED, last_modified_on=1651171728277)>,
    <User (email_address=mitch@streamsets.com, display_name=Mitch Test, status=ACTIVE, last_modified_on=1650917674930)>]

    # sch.users.get(email_address='mitch@streamsets.com')
    <User (email_address=mitch@streamsets.com, display_name=Mitch Test, status=ACTIVE, last_modified_on=1650917674930)>

    # sch.users.get_all(status='DEACTIVATED')
    [<User (email_address=kramer@streamsets.com, display_name=, status=DEACTIVATED, last_modified_on=1651171728277)>]

Inviting Users
--------------
.. _inviting_users:

Adding users is accomplished in the same section of the UI as seen above by using the 'Add New User' button, shown
below:

.. image:: ../../_static/images/manage/users_and_groups/add_new_user.png

|
Selecting 'Add New User' presents a prompt for filling in the details for the user in question, such as email address,
group membership, and the roles for the user:

.. image:: ../../_static/images/manage/users_and_groups/invite_user_details.png

|
The steps to add and invite a new user in the SDK are quite similar, requiring that you create a :py:class:`streamsets.sdk.sch_models.User`
object, specify an email address, and add any group membership or user roles before inviting the user.

To invite and add a new user to the Platform using the SDK, you first need to create a
:py:class:`streamsets.sdk.sch_models.User` instance via the :py:class:`streamsets.sdk.sch_models.UserBuilder` class -
which is retrieved from the :py:meth:`streamsets.sdk.ControlHub.get_user_builder` method. Once you've successfully built
the user and updated attributes you wish to set, pass the user object to the :py:meth:`streamsets.sdk.ControlHub.invite_user`
method:

.. code-block:: python

    user_builder = sch.get_user_builder()
    user = user_builder.build(email_address='johndeer@test.com')
    user.organization_roles = ['Connection Editor', 'Connection User', 'Topology Editor', 'Topology User']
    # Add user to three groups that exist in the organization: all, beta-testers, pipeline operators
    group_one = sch.groups.get(display_name='all')
    group_two = sch.groups.get(display_name='beta-testers')
    group_three = sch.groups.get(display_name='pipeline operators')
    user.groups = [group_one, group_two, group_three]
    response = sch.invite_user(user)

.. note::
  The :py:meth:`streamsets.sdk.ControlHub.invite_user` method will automatically update the invited user's in-memory
  representation, including adding the user's ``id``, ``organization_roles``, and ``groups``.

Updating An Existing User
-------------------------
.. _updating_users:

Updating an existing user in the UI is done by expanding the user's details, making necessary changes to attributes like
``organization_roles`` or ``groups``, and saving the changes:

.. image:: ../../_static/images/manage/users_and_groups/update_user_details.png

|
It is also possible to update a user's attributes, like ``organization_roles`` or ``groups``, from the SDK. Simply retrieve the user
you wish to update, modify the desired attribute(s), and then pass the user object to the :py:meth:`streamsets.sdk.ControlHub.update_user()`
method:

.. code-block:: python

    user = sch.users.get(email_address='mitch@streamsets.com')
    # Set the user's organization roles to be the following
    user.organization_roles = ['Engine Administrator', 'Job Operator', 'Pipeline Editor', 'Deployment Manager']
    # Add the user to a new group
    new_group = sch.groups.get(display_name='new-group')
    user.groups.append(new_group)
    response = sch.update_user(user)

Activating or Deactivating Users
--------------------------------

Users can be activated or deactivated as needed for your organization. The activation and deactivation methods in the
SDK can handle multiple users at once, or a single user at a time.

Activating a User
`````````````````

In the UI, activation of users is done by selecting the user(s) you wish to activate and using the 'Activate'
button:

.. image:: ../../_static/images/manage/users_and_groups/activate_user.png

|
In the SDK, activation requires a similar set of steps. You will first need to retrieve the user(s) you wish to activate
from your Platform organization and pass them to the :py:meth:`streamsets.sdk.ControlHub.activate_user` method.
This could be a list of several users that all need to be activated at once, or just a single user by itself:

.. code-block:: python

    # Activate single user
    user = sch.users.get(email_address='kramer@streamsets.com')
    sch.activate_user(user)

    # Activate multiple users
    users = sch.users.get_all(status='DEACTIVATED')
    sch.activate_user(*users)

Deactivating a User
```````````````````

Similarly, deactivation of users in the UI is also handled by selecting the user(s) you wish to deactivate and using
the 'Deactivate' button:

.. image:: ../../_static/images/manage/users_and_groups/deactivate_user.png

|
You will first need to retrieve the user(s) you wish to deactivate from your Platform organization and pass them
to the :py:meth:`streamsets.sdk.ControlHub.deactivate_user` method. Again, this could be a list of several users that
all need to be activated or just a single user by itself:

.. code-block:: python

    # Deactivate single user
    user = sch.users.get(email_address='mitch@streamsets.com')
    sch.deactivate_user(user)

    # Deactivate multiple users
    users = sch.users.get_all(status='ACTIVE')
    sch.activate_user(*users)

Deleting Users
--------------

Users can also be deleted from your organization as needed. This will permanently remove the user from your organization,
including the user's email address.

In the UI, deletion is accomplished by selecting the user(s) that need to be deleted and using the the 'Delete' button:

.. image:: ../../_static/images/manage/users_and_groups/delete_user.png

|
You can use the SDK to delete a single user, or multiple users at once. You will need to retrieve the user(s)
you want to delete from your organization, and then pass them into the :py:meth:`streamsets.sdk.ControlHub.delete_user`
method. You can also specify if you need to deactivate the user as well via the optional ``deactivate`` parameter (which
defaults to ``False``):

.. code-block:: python

    # Deactivate and delete a single user
    user = sch.users.get(email_address='kramer@streamsets.com')
    sch.delete_user(user, deactivate=True)

    # Delete multiple users
    users = sch.users.get_all(status='DEACTIVATED')
    sch.delete_user(*users)

Bringing It All Together
------------------------

The complete scripts from this section can be found below. Commands that only served to verify some output from the
example have been removed.

.. code-block:: python

    # ---- Retrieving Existing Users ----
    # Get a particular user
    sch.users.get(email_address='mitch@streamsets.com')
    # Get all currently deactivated users
    sch.users.get_all(status='DEACTIVATED')

    # ---- Adding Users ----
    user_builder = sch.get_user_builder()
    user = user_builder.build(email_address='johndeer@test.com')
    user.organization_roles = ['Connection Editor', 'Connection User', 'Topology Editor', 'Topology User']
    # Add user to three groups that exist in the organization: all, beta-testers, pipeline operators
    group_one = sch.groups.get(display_name='all')
    group_two = sch.groups.get(display_name='beta-testers')
    group_three = sch.groups.get(display_name='pipeline operators')
    user.groups = [group_one, group_two, group_three]
    response = sch.invite_user(user)

    # ---- Updating An Existing User ----
    user = sch.users.get(email_address='mitch@streamsets.com')
    # Set the user's organization roles to be the following
    user.organization_roles = ['Engine Administrator', 'Job Operator', 'Pipeline Editor', 'Deployment Manager']
    # Add the user to a new group
    new_group = sch.groups.get(display_name='new-group')
    user.groups.append(new_group)
    response = sch.update_user(user)

    # ---- Activating or Deactivating Users ----
    # Activate single user
    user = sch.users.get(email_address='kramer@streamsets.com')
    sch.activate_user(user)
    # Activate multiple users
    users = sch.users.get_all(status='DEACTIVATED')
    sch.activate_user(*users)

    # Deactivate single user
    user = sch.users.get(email_address='mitch@streamsets.com')
    sch.deactivate_user(user)
    # Deactivate multiple users
    users = sch.users.get_all(status='ACTIVE')
    sch.activate_user(*users)

    # ---- Deleting Users ----
    # Deactivate and delete a single user
    user = sch.users.get(email_address='kramer@streamsets.com')
    sch.delete_user(user, deactivate=True)
    # Delete multiple users
    users = sch.users.get_all(status='DEACTIVATED')
    sch.delete_user(*users)


Groups
~~~~~~

Retrieving Existing Groups
--------------------------

In the UI of a Platform Organization, you can check the existing groups as seen in the below screenshot:

.. image:: ../../_static/images/manage/users_and_groups/groups_list.png

|
Existing groups in your Platform organization are stored in the ``groups`` attribute of the
:py:class:`streamsets.sdk.ControlHub` object you've instantiated. You can further filter the available groups by
specifying items like ``group_id`` and ``display_name``:

.. code-block:: python

    # Get all groups belonging to current organization
    sch.groups

    # Retrieve a particular group
    group = sch.groups.get(group_id='beta_testers@791759af-e8b5-11eb-8015-e592a7dbb2d0')

    # Check the user instances that are members of this group
    group.users

**Output:**

.. code-block:: python

    # sch.groups
    [<Group (group_id=all@791759af-e8b5-11eb-8015-e592a7dbb2d0, display_name=all, last_modified_on=1626715168667)>,
    <Group (group_id=beta_testers@791759af-e8b5-11eb-8015-e592a7dbb2d0, display_name=beta-testers, last_modified_on=1652285645939)>,
    <Group (group_id=new_group@791759af-e8b5-11eb-8015-e592a7dbb2d0, display_name=new-group, last_modified_on=1652289828948)>,
    <Group (group_id=pipeline_operators@791759af-e8b5-11eb-8015-e592a7dbb2d0, display_name=pipeline operators, last_modified_on=1651182801634)>,
    <Group (group_id=updated_group@791759af-e8b5-11eb-8015-e592a7dbb2d0, display_name=updated group, last_modified_on=1651507406308)>]

    # group.users
    [<User (email_address=kramer@streamsets.com, display_name=, status=DEACTIVATED, last_modified_on=1651171728277)>,
    <User (email_address=mitch@streamsets.com, display_name=Mitch Test, status=ACTIVE, last_modified_on=1650917674930)>]

Creating Groups
---------------
.. _creating_groups:

Creating a new group is handled in the same section of the Platform UI, using the 'Add New Group' button as seen
below:

.. image:: ../../_static/images/manage/users_and_groups/add_new_group.png

|
Selecting 'Add New Group' presents a prompt for filling in the details for the group in question, such as group
membership and the roles for the group:

.. image:: ../../_static/images/manage/users_and_groups/new_group_details.png

|
To create a new :py:class:`streamsets.sdk.sch_models.Group` instance in a Platform organization with the
SDK, use the :py:class:`streamsets.sdk.sch_models.GroupBuilder` class. Retrieve the builder by using the
:py:meth:`streamsets.sdk.ControlHub.get_group_builder` method to instantiate it and pass the relevant details into the
:py:meth:`streamsets.sdk.sch_models.GroupBuilder.build` method:

.. code-block:: python

    group_builder = sch.get_group_builder()
    # Only display_name is required, but group_id can also be supplied if desired
    group = group_builder.build(display_name='example-group', group_id='example_group')
    # Add users to the group at creation time by specifying their IDs
    user_one = sch.users.get(email_address='mitch@streamsets.com')
    user_two = sch.users.get(email_address='kramer@streamsets.com')
    group.users = [user_one, user_two]
    # Add the 'Pipeline User' role in addition to the defaults
    group.organization_roles.append('Pipeline User')
    response = sch.add_group(group)

.. note::
  A group's ID must be unique and may only contain letters, numbers and underscores.

Updating Groups
---------------
.. _updating_groups:

Updating an existing group in the Platform UI is done by expanding the group's details, making necessary changes
to attributes like ``organization_roles`` or ``users``, and saving the changes:

.. image:: ../../_static/images/manage/users_and_groups/update_group_details.png

|
It is also possible to update a group's attributes, like ``organization_roles`` or ``users``, from the SDK. Simply retrieve the
group you wish to update, modify the desired attribute(s), and then pass the group object to the :py:meth:`streamsets.sdk.ControlHub.update_group()`
method:

.. code-block:: python

    group = sch.groups.get(display_name='example-group')
    user_to_add = sch.users.get(email_address='constanza@streamsets.com')
    group.users.append(user_to_add)
    group.organization_roles.remove('Engine Administrator')
    response = sch.update_group(group)

.. note::
  Being able to add or remove only one role at a time is a known limitation for the :py:class:`streamsets.sdk.sch_models.Group` class.
  It will be improved and expanded in a future release.
  Alternatively, setting the role list equal to a list of all roles for the group is possible as seen in previous examples.

Deleting Groups
---------------

Groups can also be deleted from your organization as needed. This will remove the group and any roles associated with
the group, meaning any group members will have the roles removed as well (unless granted elsewhere).

In the UI, deletion is accomplished by selecting the group(s) that need to be deleted and using the the 'Delete' button:

.. image:: ../../_static/images/manage/users_and_groups/delete_group.png

|
You can use the SDK to delete a single group, or multiple groups at once. You will need to retrieve the group(s)
you want to delete from your organization, and then pass them into the :py:meth:`streamsets.sdk.ControlHub.delete_group`
method:

.. code-block:: python

    # Delete a single group
    group = sch.groups.get(display_name='example-group')
    sch.delete_group(group)

    # Delete multiple groups
    groups = sch.groups.get_all(display_name='new-group')
    sch.delete_group(*groups)

.. note::
  The ``all`` group cannot be deleted from a Platform organization.

Bringing It All Together
------------------------

The complete scripts from this section can be found below. Commands that only served to verify some output from the
example have been removed.

.. code-block:: python

    # ---- Retrieving Existing Groups ----
    # Retrieve a particular group
    group = sch.groups.get(group_id='beta_testers@791759af-e8b5-11eb-8015-e592a7dbb2d0')

    # ---- Creating Groups ----
    group_builder = sch.get_group_builder()
    # Only display_name is required, but group_id can also be supplied if desired
    group = group_builder.build(display_name='example-group', group_id='example_group')
    # Add users to the group at creation time by specifying their IDs
    user_one = sch.users.get(email_address='mitch@streamsets.com')
    user_two = sch.users.get(email_address='kramer@streamsets.com')
    group.users = [user_one, user_two]
    # Add the 'Pipeline User' role in addition to the defaults
    group.organization_roles.append('Pipeline User')
    response = sch.add_group(group)

    # ---- Updating Groups ----
    group = sch.groups.get(display_name='example-group')
    user_to_add = sch.users.get(email_address='constanza@streamsets.com')
    group.users.append(user_to_add)
    group.organization_roles.remove('Engine Administrator')
    response = sch.update_group(group)

    # ---- Deleting Groups ----
    # Delete a single group
    group = sch.groups.get(display_name='example-group')
    sch.delete_group(group)
    # Delete multiple groups
    groups = sch.groups.get_all(display_name='new-group')
    sch.delete_group(*groups)

