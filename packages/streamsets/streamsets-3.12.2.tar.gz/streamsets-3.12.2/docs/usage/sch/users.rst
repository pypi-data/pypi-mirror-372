Users
=====
|
Users exist within the scope of an Organization within Control Hub. The SDK allows you to create new users, delete
existing users, update current users, and more.

Creating a new user
~~~~~~~~~~~~~~~~~~~

You can create a new :py:class:`streamsets.sdk.sch_models.User` instance using the :py:class:`streamsets.sdk.sch_models.UserBuilder`
class. Use the :py:meth:`streamsets.sdk.ControlHub.get_user_builder` method to instantiate the builder object:

.. code-block:: python

    user_builder = sch.get_user_builder()
    user = user_builder.build(id='jonsmith@test', display_name='jon smith', email_address='johnsmith@gmail.com')
    user.roles = ['Job Operator', 'Pipeline Editor', 'Organization User']     # default roles for new users
    sch.add_user(user)

Retrieving existing users
~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieving existing users from Control Hub is as simple as asking for the ``users`` attribute from the
:py:class:`streamsets.sdk.ControlHub` instance you've instantiated. You can further filter the available users by
specifying items like ``id``, ``display_name``, or ``email_address``:

.. code-block:: python

    # Get all users belonging to current organization
    sch.users

    # Get a particular user
    sch.users.get(id='jonsmith@test')

**Output:**

.. code-block:: python

    # sch.users
    [<User (id=admin@test, display_name=admin)>,
     <User (id=jonsmith@test, display_name=jon smith)>]

    # sch.users.get(id='jonsmith@test')
    <User (id=jonsmith@test, display_name=jon smith)>

Updating an existing user
~~~~~~~~~~~~~~~~~~~~~~~~~

Updating a user's attributes is, likewise, a simple task. Just retrieve the user you wish to update, modify an
attribute like ``roles`` or ``groups``, and then pass the user object into the :py:meth:`streamsets.sdk.ControlHub.update_user()` method:

.. code-block:: python

    user = sch.users.get(id='jonsmith@test')
    user.roles = ['Organization User']
    sch.update_user(user)

Deactivating existing users
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deactivating users can be done for a single user, or multiple users at once. Simply retrieve the user(s) you wish to
deactivate from Control Hub, and pass it into the :py:meth:`streamsets.sdk.ControlHub.deactivate_user` method:

.. code-block:: python

    # Deactivate single user
    user = sch.users.get(id='jonsmith@test')
    sch.deactivate_user(user)

    # Deactivate multiple users
    users = sch.users.get_all(display_name='Test User')
    sch.deactivate_user(*users)

Deleting existing users
~~~~~~~~~~~~~~~~~~~~~~~

The SDK also allows for deletion of users from an organization, the syntax for which is identical to deactivation
of a user. Deletion can be done for a single user, or multiple users at once. Simply retrieve the user you wish to
deactivate from Control Hub, and pass it into the :py:meth:`streamsets.sdk.ControlHub.delete_user` method:

.. code-block:: python

    # Deactivate and delete a single user
    user = sch.users.get(id='jonsmith@test')
    sch.delete_user(user, deactivate=True)

    # Delete multiple users
    users = sch.users.get_all(display_name='Test User')
    sch.delete_user(*users)


