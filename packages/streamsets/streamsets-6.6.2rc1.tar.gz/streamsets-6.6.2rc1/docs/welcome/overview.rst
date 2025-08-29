Overview
========
|

**Prerequisites**

In order to begin using the StreamSets Platform SDK for Python, there are a few prerequisite criteria
that must be met:

* The StreamSets Platform SDK for Python must be :ref:`installed <installation>`.
* A Python 3.4+ interpreter and the pip3 package manager must both be installed on the machine where the SDK will be
  used.
* Have access to a `StreamSets Platform <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/OrganizationSecurity/MyOrganization_title.html#concept_bdc_yqt_lpb>`_
  instance with a user account in your organization. Note: Make sure the user account has proper access within the organization.
  For more details refer to the StreamSets Documentation for `roles <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/OrganizationSecurity/Roles.html#concept_xgr_h1d_dx>`_ and `permissions <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/OrganizationSecurity/Permissions.html#concept_e5n_fgm_wy>`_ .
* Optional - If you wish to run StreamSets Pipelines, you need an engine. StreamSets has three engines: Data Collector,
  Transformer and Transformer for Snowflake. You can either deploy and launch a Data Collector or a Transformer, or use
  Transformer for Snowflake directly.
  For more details refer to the `StreamSets Platform Documentation <https://docs.streamsets.com/portal/#platform-controlhub/controlhub/UserGuide/Engines/Overview.html#concept_r1f_4kx_t4b>`_ .

Once you have satisfied the above requirements, you can utilize the SDK by launching a Python3 interpreter shell and
importing the relevant modules you wish to use:

.. code-block:: bash

    $ python3
    Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 26 2018, 19:50:54)
    [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from streamsets.sdk import ControlHub

You now have a Python3 interpreter running with the ControlHub module imported from the StreamSets Platform SDK for Python!
