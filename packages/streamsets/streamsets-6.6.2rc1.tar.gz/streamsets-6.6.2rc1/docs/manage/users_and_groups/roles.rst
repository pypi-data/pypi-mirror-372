Roles
=====
|
StreamSets Platform provides several different role types that allow you to customize or restrict the level of access
that users in your organization have.

For more details on the types of roles available and the access they grant, please refer to the
`StreamSets Platform Documentation <https://docs.streamsets.com/portal/platform-controlhub/controlhub/UserGuide/OrganizationSecurity/Roles.html#concept_xgr_h1d_dx>`_.

Selecting a User's Roles at Creation Time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As shown in the :ref:`Inviting Users<inviting_users>` section, a User's roles can be selected at creation time in the
SDK by setting the the ``organization_roles`` attribute equal to a list of roles for that user. You can then pass the :py:class:`streamsets.sdk.sch_models.User`
instance to the :py:meth:`streamsets.sdk.ControlHub.invite_user` method:

.. code-block:: python

    user_builder = sch.get_user_builder()
    user = user_builder.build(email_address='johndeer@test.com')
    user.organization_roles = ['Connection Editor', 'Connection User', 'Topology Editor', 'Topology User']
    response = sch.invite_user(user)

The SDK utilizes the same naming conventions for the roles as the Platform UI. A list of the available roles
can be found in the Platform Documentation.

Updating an Existing User's Roles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As shown in the :ref:`Updating An Existing User<updating_users>` section, you can also update the roles of an existing
user in the SDK. Similar to selecting roles at user creation time, you can update an existing user's roles by
setting the the ``organization_roles`` attribute equal to a list of roles the user should have and passing the updated :py:class:`streamsets.sdk.sch_models.User`
instance to the :py:meth:`streamsets.sdk.ControlHub.update_user()` method:

.. code-block:: python

    user = sch.users.get(email_address='kramer@streamsets.com')
    # Set the user's roles to be the following
    user.organization_roles = ['Engine Administrator', 'Job Operator', 'Pipeline Editor', 'Deployment Manager']
    response = sch.update_user(user)

Selecting a Group's Roles at Creation Time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As seen in the :ref:`Creating Groups<creating_groups>` section, the roles assigned to a group can be specified at
creation time. Utilize the :py:meth:`streamsets.sdk.sch_models.Roles.append` and :py:meth:`streamsets.sdk.sch_models.Roles.remove`
methods to add and remove roles from the group, and then pass the :py:class:`streamsets.sdk.sch_models.Group` instance
to the :py:meth:`streamsets.sdk.ControlHub.add_group` method:

.. code-block:: python

    group_builder = sch.get_group_builder()
    group = group_builder.build(display_name='example-group', group_id='example_group')
    # Add the 'Pipeline User' role and remove the 'Engine Administrator' role
    group.organization_roles.append('Pipeline User')
    group.organization_roles.remove('Engine Administrator')
    response = sch.add_group(group)

Updating an Existing Group's Roles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also update the roles of an existing group, as shown in the :ref:`Updating Groups<updating_groups>` section.
Similarly to setting a group's roles during creation, utilize the :py:meth:`streamsets.sdk.sch_models.Roles.append` and
:py:meth:`streamsets.sdk.sch_models.Roles.remove` methods to add and remove roles from the group after retrieving the
group in question from Platform. Once the updates have been made, pass the :py:class:`streamsets.sdk.sch_models.Group`
instance to the :py:meth:`streamsets.sdk.ControlHub.update_group` method:

.. code-block:: python

    group = sch.groups.get(display_name='example-group')
    group.organization_roles.remove('Deployment Manager')
    response = sch.update_group(group)

.. note::
  Being able to add or remove only one role at a time is a known limitation for the :py:class:`streamsets.sdk.sch_models.Group`
  class. It will be improved and expanded in a future release.

Project Roles
~~~~~~~~~~~~~

.. _project_roles:

If the Projects feature is enabled in your organization, you will be able to grant Users and Groups project-level
roles. These roles behave the same as organization roles, but grant users a role across all projects they are
assigned to. You can further control this by assigning them appropriate permissions to a resource.

In the UI, you can see a section for project roles.

.. image:: ../../_static/images/manage/users_and_groups/project_roles.png

This behaves exactly like organization roles.

In the SDK, you can use :py:attr:`streamsets.sdk.sch_models.User.project_roles` and :py:attr:`streamsets.sdk.sch_models.Group.project_roles`
to modify project roles for a user or group. The usage and behavior is the same as that of :py:attr:`streamsets.sdk.sch_models.User.organization_roles`
and :py:attr:`streamsets.sdk.sch_models.Group.organization_roles`.

.. code-block:: python

    # give a user the "Connection Editor" role.
    user = sch.users.get(email_address="user.in@project")
    user.project_roles.append("Connection Editor")
    sch.update_user(user)

    # remove the "Deployment Manager" role from a group
    group = sch.groups.get(display_name="not deployment managers")
    group.project_roles.remove("Deployment Manager")
    sch.update_group(group)
