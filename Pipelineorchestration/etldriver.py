#!/anaconda3/envs/dbconnect/python.exe

import pyspark
from pyspark.sql import SparkSession
from pathlib import Path
import logging
import logging.config
import configparser
import time
from pathlib import Path
import sys

path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
logging.info(path)

try:
    sys.path.insert(1, path+"/Pipelineorchestration/eod_load") # the type of path is string
    sys.path.insert(2, path+"/Pipelineorchestration/analytical_processing")
    sys.path.insert(3, path+"/Pipelineorchestration/preprocessing")
    sys.path.insert(4, path+"/Pipelineorchestration/job_tracker")
    # /databricks/python/lib/python3.7/site-packages/Pipelineorchestration/

    from etl_load import ETLLoad
    from analytical_transformations import AnalyticalETL
    from process_raw import Preprocess
    from Tracker import Tracker
except (ModuleNotFoundError, ImportError) as e:
    print("{} fileure".format(type(e)))
else:
    print("Import succeeded")




logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(funcName)s :: %(lineno)d \
:: %(message)s', level = logging.INFO)



config = configparser.ConfigParser()
config.read('config.cfg')
#config.read_file(open(f"{Path(__file__).parents[0]}/Pipelineorchestration/config.cfg"))

def create_sparksession():
    """
    Initialize a spark session
    """
    return SparkSession.builder.\
           appName("Spring Capital Analytical ETL").\
           getOrCreate()


            

def main(job: str = "",**kwargs):
    """
    Args:
        job: Job name
        **kwargs: Other arguments of a job
    """
    """
    Driver code to perform the following steps
    1. Works on the pre-processed parquet files and transforms and loads the end of day trade and quote records
    2. Executes the final analytical_etl function that uses SparkSQL and Python to build an ETL job 
        that calculates the following results for a given day:
        - Latest trade price before the quote.
        - Latest 30-minute moving average trade price, before the quote.
        - The bid/ask price movement from previous day’s closing price
    """
    logging.debug("\n\nSetting up Spark Session...")
    spark = create_sparksession()
    spark_context = spark.sparkContext
    pre_process= Preprocess(spark,spark_context)

    etl_load = ETLLoad(spark)
    analy_etl = AnalyticalETL(spark)

    # cleaning tables
    logging.debug("\n\nCleaning Hive Tables...")
    spark.sql("DROP TABLE IF EXISTS trade")
    spark.sql("DROP TABLE IF EXISTS temp_trade")
    spark.sql("DROP TABLE IF EXISTS temp_trade_mov_avg")
    spark.sql("DROP TABLE IF EXISTS prev_trade")
    spark.sql("DROP TABLE IF EXISTS prev_temp_last_trade")
    spark.sql("DROP TABLE IF EXISTS temp_quote")
    spark.sql("DROP TABLE IF EXISTS quotes")
    spark.sql("DROP TABLE IF EXISTS quotes_union")
    spark.sql("DROP TABLE IF EXISTS trades_latest")
    spark.sql("DROP TABLE IF EXISTS quotes_update")
    

    # Modules in the project
    modules = {
         "raw csv": pre_process.process_csv,
         "raw json": pre_process.process_json,
         "eod trade": etl_load.etl_load_trade,
         "eod quote" : etl_load.etl_load_quote,
         "analytical_quote": analy_etl.anaytical_etl
    }

    for file in modules.keys():
        try:
           logging.info("Processing "+file)
           modules[file]()
        except Exception as e:
           print(e)
           logging.error(" Error encountered while processing "+file)
           return 
    
    

        

# Entry point for the pipeline
if __name__ == "__main__":
    #main()
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--job", type=str)
    parser.add_argument("--date_range", default=",")

    # Parse the cmd line args
    args = parser.parse_args()
    args = vars(args)
   # logging.info("Cmd line args:\n{}".format(json.dumps(args, sort_keys=True, indent=4)))

    main(**args)

    #trade_date = config.get('PRODUCTION', 'processing_date')

    trade_date = "2020-08-06"
    
    logging.info("Updating the job status in the POSTGRES Table")
    tracker = Tracker("analytical_etl", trade_date)
    try:
        logging.info("Updating the job status")
        tracker.update_job_status("success")
    except Exception as e:
        tracker.update_job_status("failed")
        logging.error("Error while performing operation in the table {}".format(e))
    
    logging.info("ALL DONE!\n")
  
    