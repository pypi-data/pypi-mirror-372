Tools
=====

StreamSets Toolkit ships with several command line tools. Some of them can be used
as examples on which you can base your work and others are standalone tools for the
StreamSets ecosystem.

Sqoop Import
------------

`Apache Sqoop <http://sqoop.apache.org>`_ is a tool designed for efficiently transferring
bulk data between Apache Hadoop and structured datastores such as relational databases.
StreamSets Toolkit contains console command `streamsets-sqoop-import` that can create
Data Collector pipelines that are roughly functionally equivalent to the given Sqoop command.

The `streamsets-sqoop-import` tool accepts most of Sqoop's command line arguments plus a few
others that are specific to Data Collector itself. To import the following Sqoop command:

.. code-block:: console

    $ sqoop import \
        --username demo \
        --password demo \
        --connect jdbc:mysql://demo.streamsets.net/employees \
        --table employees \
        --hive-import

Instead of calling `sqoop import`, call the `streamsets-sqoop-import` command with all the
arguments that you used for Sqoop:

.. code-block:: console

    $ streamsets-sqoop-import  \
        --username demo \
        --password demo \
        --connect jdbc:mysql://demo.streamsets.net/employees \
        --table employees \
        --hive-import

This command assumes that you're running Data Collector locally on your machine and it will
create and import the pipeline there. To import the pipeline to a Data Collector running on a different
machine, use the `--sdc-url` argument with the URL to the remote Data Collector.

List of all Data Collector specific arguments:

- `--sdc-url` URL to Data Collector where generated pipeline should be uploaded. Default value
  is `http://localhost:18630/`.
- `--sdc-stagelib` Name of stage library that should be used for all Hadoop stages. Primarily
  used to specify Hadoop distribution and version. Example value is `streamsets-datacollector-cdh_5_12-lib`
  for CDH 5.12 or `streamsets-datacollector-mapr_5_2-lib` for MapR 5.2.
- `--sdc-username` Username for the Data Collector. Default value is `admin`.
- `--sdc-password` Password for the Data Collector. Default value is `admin`.
- `--sdc-hive` HiveServer2 URL to use when importing into Hive. Default value is
  `jdbc:hive2://localhost:10000/default`

Don't hesitate to let us know how well `streamsets-sqoop-import` works for you!
