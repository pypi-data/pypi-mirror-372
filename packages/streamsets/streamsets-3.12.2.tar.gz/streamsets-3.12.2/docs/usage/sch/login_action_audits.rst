Login and Action audits
=======================
|
Within an organization, Control Hub keeps track of a number of different actions and events through various audits -
including user login and user/group actions.

The SDK allows retrieval of all login audits for the current user within Control Hub. Simply reference the
:py:attr:`streamsets.sdk.ControlHub.login_audits` attribute from the :py:class:`streamsets.sdk.ControlHub` object. This will
retrieve the login audits for the user you provided when authenticating with Control Hub from the SDK:

.. code-block:: python

    sch.login_audits

**Output:**

.. code-block:: python

    [<LoginAudit (user_id=admin@test, ip_address=0:0:0:0:0:0:0:1, login_timestamp=1586455914797, logout_timestamp=0)>,
     <LoginAudit (user_id=admin@test, ip_address=0:0:0:0:0:0:0:1, login_timestamp=1586455135790, logout_timestamp=0)>]

Likewise, the SDK allows retrieval of action audits taken by, or affecting, the current user. Simply reference the
:py:attr:`streamsets.sdk.ControlHub.action_audits` attribute from the :py:class:`streamsets.sdk.ControlHub` object. This will
retrieve the action audits for the user you provided when authenticating with Control Hub from the SDK:

.. code-block:: python

    sch.action_audits

**Output:**

.. code-block:: python

    [<ActionAudit (affected_user_id=admin@test,
                   action=USER_SET_PASSWORD,
                   time=1586385312431,
                   ip_address=0:0:0:0:0:0:0:1)>,
     <ActionAudit (affected_user_id=admin@test,
                   action=GROUP_USER_UPDATE,
                   time=1586385282216,
                   ip_address=0:0:0:0:0:0:0:1)>]

