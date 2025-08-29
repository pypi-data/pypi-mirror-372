Authentication
==============
|

The StreamSets Platform SDK for Python uses API Credentials for authentication.

For more details, refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/OrganizationSecurity/APICredentials_title.html#concept_vpm_p32_qqb>`_.

Creating API Credentials
~~~~~~~~~~~~~~~~~~~~~~~~

The initial API credentials needed to authenticate with the Platform via the SDK will need to be generated from within the Platform's UI.

Once the initial API credentials have been created, it is possible to create additional API credentials directly from the SDK.

From the UI
-----------
Using a web browser, log into the StreamSets Platform.

In the UI, API Credentials are presented as seen below:

.. image:: ../_static/images/welcome/api_credentials.png
|

Create new API credentials by referring to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/OrganizationSecurity/APICredentials_title.html#task_jsq_h3f_qqb>`_.

From the SDK
------------
Once you have an initial set of API credentials created and can authenticate successfully with the Platform,
you can also generate additional API credentials directly from the SDK.

To create a new set of API credentials and add them to the Platform, you will need to use the :py:class:`streamsets.sdk.sch_models.ApiCredentialBuilder` class.

Call the :py:meth:`streamsets.sdk.ControlHub.get_api_credential_builder` method to instantiate the builder instance.
Then, call the :py:meth:`streamsets.sdk.sch_models.ApiCredentialBuilder.build` method while supplying a ``name`` value for the API credentials to be created.
Finally, take the resulting :py:class:`streamsets.sdk.sch_models.ApiCredential` instance and pass it to the :py:meth:`streamsets.sdk.ControlHub.add_api_credential` method to generate the API credentials:

.. code-block:: python

    api_cred_builder = sch.get_api_credential_builder()
    api_credential = api_cred_builder.build(name='H.E. Pennypacker API Creds')
    sch.add_api_credential(api_credential)

The :py:meth:`streamsets.sdk.ControlHub.add_api_credential` method will update the api_credential instance directly in-memory without needing to retrieve or refresh it.

.. warning::
   The ``credential_id`` and ``auth_token`` values for a set of API credentials are private key values and should be safeguarded as sensitive passwords.
   These values are not retrievable after the API credentials have been created.
   If the resulting API credentials are deleted from local memory and the values are not stored, they will be lost.

For the purpose of this documentation, the ``credential_id`` and ``auth_token`` attributes of the API credentials will
be referred as <credential ID> and <token> respectively.

Connecting to Control Hub
~~~~~~~~~~~~~~~~~~~~~~~~~

Connect to Control Hub by creating an instance of :py:class:`streamsets.sdk.ControlHub`, passing in
the API Credentials.

.. code-block:: python

    # Connect to the StreamSets Platform.
    sch = ControlHub(credential_id=<credential ID>, token=<token>)
