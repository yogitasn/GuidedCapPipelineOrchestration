## Table of contents
* [General Info](#general-info)
* [Description](#description)
* [Technologies](#technologies)
* [Setup](#setup)
* [Screenshot](#screenshot)


## General Info
Step Five: Pipeline Orchestration for Guided Capstone project.


<hr/>

## Description
In this project we need to orchestrate the pipeline, connecting all of the individual components into an end-to-end data pipeline. In the real world, data processing jobs are typically organized into automated workflows.

<hr/>

## Technologies
The Project is created with the following technologies:
* Azure Storage-Containers/File Share: To store the raw data.
* Databricks-connect: Allow the user to step through and debug Spark code in the local environment and execute it on remote Azure Databricks cluster (7.3 LTS) - Local Execution.
    * [Reference](https://docs.databricks.com/dev-tools/databricks-connect.html)
       * Python 3.7.5 (which matches the remote cluster python version)

* Azure Database for Postgres (Single Server): To store the job tracking status in the Postgres.

    


## Setup

<hr/>

1. Create a Databricks cluster (7.3 LTS) and notebook and run the below code to mount the raw data files from Azure Blob Container to DBFS:

```
storageAccountName = ""
storageAccountAccessKey = ""
blobContainerName = ""

#databricks
if not any(mount.mountPoint == '/mnt/FileStore/raw/' for mount in dbutils.fs.mounts()):
  try:
    dbutils.fs.mount(
    source = "wasbs://{}@{}.blob.core.windows.net".format(blobContainerName, storageAccountName),
    mount_point = "/mnt/FileStore/raw/",
    extra_configs = {'fs.azure.account.key.' + storageAccountName + '.blob.core.windows.net': storageAccountAccessKey}
  )
  except Exception as e:
    print("already mounted. Try to unmount first")

display(dbutils.fs.ls("dbfs:/mnt/FileStore/raw/"))

```

*  Local Environment Setup using Databricks connect:
  ```
  * Reference: https://docs.databricks.com/dev-tools/databricks-connect.html
    * Your Spark job is planned local but executed on the remote cluster
    * Allow the user to step through and debug Spark code in the local environment

    * requirements.txt file example:
    databricks-connect(7.3.7): The databricks-connect version should match the Databricks cluster version i.e. 7.3 LTS
    * Configuration
        * The trick is one cannot mess up the delicate databricks-connect and pyspark versions

    * Test with this example:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.appName("test").getOrCreate()
    print(spark.range(100).count())  # it executes on the cluster, where you can see the record

  ```

2. Navigate to the project folder and execute the following commands:


  * <b>Local Execution</b>: 

    * The driver will call the transformation code for executing the ETL load to load end of day daily records for trade and quote and finally perform analytical transformations on those records to get the final quote table

      ```
      python etldriver.py

      ```


* <b>Execution in Production</b>

1. Execute the below commands to create a Python package file:

```
Setup file
Tutorial:
  http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/quickstart.html
rm -rf dist/
python setup.py sdist bdist_wheel
cd ..
pip install -I Pipelineorchestration/dist/Pipelineorchestration-1.0-py3-none-any.whl  # Must be outside the project root
cd Pipelineorchestration
```

2. Install the .whl file in the Databricks cluster created above.
3. Create a notebook and paste and execute the following commands:

```
from Pipelineorchestration import main

job="test"
date_range="2020-01-01,2020-01-02"

main(
   job=job,
   date_range=date_range
)


```
3. Create a job and attach the above notebook to the job.
4. Execute the spark job.

<hr/>

* <b>Python files</b>:

<hr/>

   * <b>preprocessing/process_raw.py</b>: Preprocessing step to process the trade and quote records from stock exchange daily submissions files in a semi-structured text format.

   * <b>eod_data/etl_load.py</b>: After preprocessing the incoming data from the exchange, we need to further process and load the final quote and trade records.

   * <b>analytical_processing/analytical_transformations.py</b>: Logic to build analytical quote table based on current and previous day trade calculations.

   * <b>Tracker/Tracker.py</b>: Python utility function to create a job tracking table and track the status of the job run.

<hr/>



### Screenshot

Refer to the Pipeline Orchestration document for detailed steps and screenshots

