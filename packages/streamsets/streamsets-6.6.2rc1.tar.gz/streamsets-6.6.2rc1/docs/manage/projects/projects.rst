Managing Projects
=================
|

The SDK allows you to manage projects for your organization. This includes creating or deleting projects, managing users and groups
that have access to a project.

Creating A Project
~~~~~~~~~~~~~~~~~~

To create a Project on the Platform UI, you should go to Manage > Projects and click on the ``+`` icon.

.. image:: ../../_static/images/manage/projects/create_project.png
|

To create a Project via the SDK, you need to instantiate a new instance of :py:class:`streamsets.sdk.sch_models.ProjectBuilder`
to create a new instance of :py:class:`streamsets.sdk.sch_models.Project`.

To instantiate the builder instance use :py:meth:`streamsets.sdk.ControlHub.get_project_builder` method.
You can then call the :py:meth:`streamsets.sdk.sch_models.ProjectBuilder.build` method to create the new Project by supplying the ``name``
and the optional ``description`` parameter.

After instantiating the object, you can add it to Platform via the :py:meth:`streamsets.sdk.ControlHub.add_project`.

.. code-block:: python

    # Instantiate the ProjectBuilder
    project_builder = sch.get_project_builder()

    # build the project by passing name, and optionally a description
    project = project_builder.build(name='Secret project', decription='Nothing to see')

    # add the project to Platform
    sch.add_project(project)

Manage User And Group Access For Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Managing the project roles for a user or group is explained in the :ref:`Project Roles<project_roles>` section.

Adding Users and Groups To Project
----------------------------------

After creating a project in the step above, we are now ready to add users and groups to a project.

To do this you can use the following methods, :py:meth:`streamsets.sdk.sch_models.Project.add_user`
and :py:meth:`streamsets.sdk.sch_models.Project.add_group`.

You can pass one or more instances of :py:class:`streamsets.sdk.sch_models.User` or :py:class:`streamsets.sdk.sch_models.Group`
to the respective methods to add them to a project.

.. code-block:: python

    # get a user to add to a project
    user = sch.users.get(email_address="some.person@company.com")

    # add the user to a project
    project.add_user(user)

    # you can add multiple users in a single call
    project.add_user(user1, user2)

    # get a group to add to a project
    group = sch.groups.get(display_name='many-persons')

    # add the group to the project
    project.add_group(group)

    # you can add multiple groups in a single call
    project.add_group(group1, group2)

Listing Users and Groups In Project
-----------------------------------

To list the users and groups in a project you can use the :py:attr:`streamsets.sdk.sch_models.Project.users` and
:py:attr:`streamsets.sdk.sch_models.Project.groups` respectively.

.. code-block:: python

    # list users
    project.users
    # Output: [User(name=...), User(name...)]

    # list groups
    project.groups
    # Output: [Group(display_name=...), Group(display_name=...)]

Both attributes return a :py:class:`streamsets.sdk.utils.SeekableList` and it is possible to filter for users or groups based on their attributes.

Removing Users and Groups From Project
--------------------------------------

To remove a user or group from a project you can use the following methods: :py:meth:`streamsets.sdk.sch_models.Project.remove_user`
and :py:meth:`streamsets.sdk.sch_models.Project.remove_group`.

You can pass one or more instances of :py:class:`streamsets.sdk.sch_models.User` or :py:class:`streamsets.sdk.sch_models.Group`
to the respective methods to remove them from a project.

.. code-block:: python

    # remove a user
    project.remove_user(user)

    # remove multiple users
    project.remove_user(user1, user2)

    # remove a group
    project.remove_group(group)

    # remove multiple groups
    project.remove_group(group1, group2)

Listing Projects
~~~~~~~~~~~~~~~~

You can use the :py:attr:`streamsets.sdk.ControlHub.projects` to list all the projects in your Organization.
This returns an instance of :py:class:`streamsets.sdk.utils.SeekableList` containing instances of
:py:class:`streamsets.sdk.sch_models.Project`.

.. code-block:: python

    # list projects
    sch.projects
    # Output: [Project(name=..), Project(name=...)]

    # get a particular project
    project_x = sch.projects.get(name='project x')

Switching Project And Organization Views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the Platform UI, you start with a organization-level view by default. You can switch to a particular project's view by clicking
on the option on the top bar of the screen and choosing which project to switch to. You can also click on the organization
to switch back to an organization-level view.

.. image:: ../../_static/images/manage/projects/switch_projects.png
|

In the SDK, we maintain a similar experience to the UI by starting with an organization-level view. We then allow the user to choose a project and switch to that project's view.

This is achieved with the :py:attr:`streamsets.sdk.ControlHub.current_project` property. This property defaults to ``None``
and can then be set to an instance of :py:class:`streamsets.sdk.sch_models.Project` to get that project's view.
It can then be reset to ``None`` to return to an organization-level view.

.. code-block:: python

    # initialise a ControlHub instance
    sch = ControlHub(...)

    # the default view is always organization-level
    sch.current_project is None
    # Output: True

    # get a project that we can switch to
    project = sch.projects.get(name='my project')

    # switch to the project view
    sch.current_project = project

    # SDK usage is the same inside a project when this attribute is set

    # switch to organization-level view
    sch.current_project = None

Updating A Project
~~~~~~~~~~~~~~~~~~

Updating a project refers to updating the ``name`` and ``description`` of a project. We can do this by updating the values of those
attributes of a :py:class:`streamsets.sdk.sch_models.Project` instance and then calling the :py:meth:`streamsets.sdk.ControlHub.update_project`
method to update it on Platform.

.. code-block:: python

    # get a project to update
    project = sch.projects.get(name='please update this name')

    # set a new name or description
    project.name = 'fantastic new name'
    project.description = 'some description'

    # update it on platform
    sch.update_project(project)

Deleting A Project
~~~~~~~~~~~~~~~~~~

A project can be deleted by passing a :py:class:`streamsets.sdk.sch_models.Project` instance to the
:py:meth:`streamsets.sdk.ControlHub.delete_project` method.

.. code-block:: python

    # get a project to delete
    project = sch.projects.get(name='delete this')

    # call delete on platform
    sch.delete_project(project)

    # you can delete multiple projects at the same time
    projects_to_delete = sch.projects.get_all(description='unused')
    sch.delete_project(*projects_to_delete)

Bringing It All Together
~~~~~~~~~~~~~~~~~~~~~~~~

The complete scripts from this section can be found below.

.. code-block:: python

    # Retrieve all projects
    sch.projects

    # switching to project's view
    project = sch.projects.get(name='some project')
    sch.current_project = project

    # switching to an organization-level view
    sch.current_project = None

    # Creating a project
    project_builder = sch.get_project_builder()
    project = project_builder.build(name='some name', description='optional description')
    sch.add_project(project)

    # Updating a project's name or description
    project.name = 'new name'
    project.description = 'new description'
    sch.update_project(project)

    # Deleting a project
    sch.delete_project(project)

    # Retrieve users/groups in a project
    project.users
    project.groups

    # Add users/groups to a project
    # project.add_user(user1, user2)
    # project.add_group(group1, group2)

    # Remove users/groups from a project
    # project.remove_user(user1, user2)
    # project.remove_group(group1, group2)
