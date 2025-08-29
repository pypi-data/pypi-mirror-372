Subscriptions
=============
|
A subscription listens for Control Hub events and then completes an action when those events occur. The SDK makes it
possible to interact with Subscriptions including creation, deletion, and even reading the events from a
subscription.

Creating a Subscription
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create a new :py:class:`streamsets.sdk.sch_models.Subscription` instance within Control Hub via the
:py:class:`streamsets.sdk.sch_models.SubscriptionBuilder` class. Use the :py:meth:`streamsets.sdk.ControlHub.get_subscription_builder`
method to instantiate the builder object:

.. code-block:: python

    subscription_builder = sch.get_subscription_builder()

    subscription_builder.add_event(event_type='Pipeline Committed')
    subscription_builder.set_email_action(recipients=['fake@fake.com'],
                                          subject='{{PIPELINE_NAME}} pipeline was committed',
                                          body=('{{PIPELINE_COMMITTER}} committed the {{PIPELINE_NAME}} pipeline '
                                                'on {{PIPELINE_COMMIT_TIME}}.'))
    subscription = subscription_builder.build(name='Sample Subscription')
    sch.add_subscription(subscription)

Retrieving a Subscription
~~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve an existing subscription from Control Hub simply reference the ``subscriptions`` attribute:

.. code-block:: python

    sch.subscriptions

**Output:**

.. code-block:: python

    [<Subscription (id=9c513e23-0a0c-433f-91a3-646ecb481f48:admin, name=Error Message)>,
     <Subscription (id=f0240043-5d32-4645-b15b-1a37e7b78520:admin, name=Job Error)>,
     <Subscription (id=4accdcbc-9c74-4b5e-a224-1838c0149c33:admin, name=Pipeline Finish)>,
     <Subscription (id=fef279f1-4b3b-4e83-b99a-4250aa280361:admin, name=Pipeline/Job Name Alert)>,
     <Subscription (id=fe1f5b87-86bb-430c-bc14-9f2769546512:admin, name=SDC Down Alert)>]

You can also filter the results by attributes like ``name`` or ``id`` to retrieve a specific subscription:

.. code-block:: python

    sch.subscriptions.get(name='SDC Down Alert')

**Output:**

.. code-block:: python

    <Subscription (id=fe1f5b87-86bb-430c-bc14-9f2769546512:admin, name=SDC Down Alert)>

Getting the events from a Subscription object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've retrieved a specific subscription :py:class:`streamsets.sdk.sch_models.Subscription` that you're interested
in, you can then introspect on the events that exist within that subscription:

.. code-block:: python

    subscription.events

**Output:**

.. code-block:: python

    [<SubscriptionEvent (event_type=Job Status Change, filter=)>,
     <SubscriptionEvent (event_type=Data SLA Triggered, filter=)>,
     <SubscriptionEvent (event_type=Pipeline Committed, filter=)>,
     <SubscriptionEvent (event_type=Pipeline Status Change, filter=)>,
     <SubscriptionEvent (event_type=Report Generated, filter=)>,
     <SubscriptionEvent (event_type=Data Collector not Responding, filter=)>]

You can also filter the events by the ``event_type``:

.. code-block:: python

    event = subscription.events.get(event_type='Pipeline Committed')
    event

**Output:**

.. code-block:: python

    <SubscriptionEvent (event_type=Pipeline Committed, filter=)>

Getting the action from a Subscription object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to retrieving the events from a subscription, you can also view the action set for a specific subscription by
referencing the :py:attr:`streamsets.sdk.sch_models.Subscription.action` attribute:

.. code-block:: python

    action = subscription.action
    action

**Output:**

.. code-block:: python

    <SubscriptionAction (event_type=EMAIL)>

Update an existing Subscription
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updating an existing subscription is similar to creating a new subscription for the first time. It makes use of the
:py:class:`streamsets.sdk.sch_models.SubscriptionBuilder` class to import the existing subscription object, which then
allows the subscription to be modified. Once the subscription has been modified as desired, the :py:meth:`streamsets.sdk.sch_models.SubscriptionBuilder.build`
method is used to construct the subscription instance which can then be passed to Control Hub via the
:py:meth:`streamsets.sdk.ControlHub.update_subscription` method:

.. code-block:: python

    subscription = sch.subscriptions.get(name='Sample Subscription')
    # Import Subscription into builder
    subscription_builder = sch.get_subscription_builder()
    subscription_builder.import_subscription(subscription)
    # Remove existing event
    subscription_builder.remove_event(event_type='Pipeline Committed')
    # Add a new Job Status Change Event
    subscription_builder.add_event(event_type='Job Status Change', filter="${{JOB_ID=='{}'}}".format(job.job_id))
    # Change action to Webhook action
    subscription_builder.set_webhook_action(uri='https://google.com')
    # Build the subscription
    subscription = subscription_builder.build(name='Sample Subscription updated')
    # Update the Subscription on Control Hub instance
    sch.update_subscription(subscription)

Deleting an existing Subscription
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deleting an existing subscription is as simple as retrieving the :py:class:`streamsets.sdk.sch_models.Subscription`
object from Control Hub, and passing it into the :py:meth:`streamsets.sdk.ControlHub.delete_subscription` method:

.. code-block:: python

    subscription = sch.subscriptions.get(name='Sample Subscription updated')
    sch.delete_subscription(subscription)

Acknowledging a subscription error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Errors generated by subscriptions can also be acknowledged directly from the SDK. Simply retrieve the subscription
with the error from Control Hub, and pass the object into the :py:meth:`streamsets.sdk.ControlHub.acknowledge_event_subscription_error`
method:

.. code-block:: python

    subscription = sch.subscriptions.get(name='Sample Subscription')
    # Check the current error message for this subscription, if any
    subscription.error_message

    sch.acknowledge_event_subscription_error(subscription)
    subscription.error_message

**Output:**

.. code-block:: python

    # subscription.error_message
    'Failed to trigger email action for event fbee1816-6c72-40ec-a432-e19b5ccac891:admin due to: Issues:
    [APP_ISSUES_01 - Exception: com.streamsets.datacollector.email.EmailException: javax.mail.SendFailedException:
    Invalid Addresses;\n  nested exception is:\n\tcom.sun.mail.smtp.SMTPAddressFailedException: 553 5.1.2
    The recipient address <fake@fake.com> is not a valid RFC-5321 address. x203sm9391603pgx.61 - gsmtp\n]'

    # sch.acknowledge_event_subscription_error(subscription)
    <sdk.sch_api.Command at 0x111c50eb8>

    # subscription.error_message
    None

Retrieving subscription audits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Subscription events are also audited, allowing you to review changes and updates made to subscriptions directly in the
SDK. To retrieve subscription audit events from Control Hub, simply reference the :py:attr:`streamsets.sdk.ControlHub.subscription_audits`
attribute for the :py:class:`streamsets.sdk.ControlHub` object you've instantiated:

.. code-block:: python

    sch.subscription_audits

**Output:**

.. code-block:: python

    [<SubscriptionAudit (subscription_name='pipeline',
                         event_name='PIPELINE_COMMITTED',
                         external_action_type='WEBHOOKV1',
                         created_time=1607548034094)>,
     <SubscriptionAudit (subscription_name='new pipeline',
                         event_name='PIPELINE_COMMITTED',
                         external_action_type='WEBHOOKV1',
                         created_time=1607548034094)>]


