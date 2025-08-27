# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2021, 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import base64
import json
from abc import abstractmethod


from ibm_metrics_plugin.common.utils.metrics_logger import MetricLogger
from ibm_metrics_plugin.common.utils.datetime_util import DateTimeUtil
from ibm_wos_utils.joblib.utils.db_utils import DbUtils


class FairnessStore():
    """Class used to store fairness results."""

    def __init__(self, spark, data_source, data_table):
        self.data_store = self.__get_data_store(
            spark=spark, data_source=data_source, data_table=data_table)

    def store_fairness_results(self, fairness_df):
        self.data_store.store_fairness_results(fairness_df)


    def __get_data_store(self, spark, data_source, data_table):
        data_stores = [HiveDataStore(spark=spark, data_source=data_source, data_table=data_table), JdbcDataStore(
            spark=spark, data_source=data_source, data_table=data_table)]

        return next((d for d in data_stores if d.is_supported()), None)

class DataStore():
    """Interface for the different types of data stores"""

    def __init__(self, spark, data_source, data_table):
        self.logger = MetricLogger(__name__)
        self.spark = spark
        self.data_source = data_source
        self.data_table = data_table

    @abstractmethod
    def is_supported(self):
        pass

    @abstractmethod
    def store_fairness_results(self, fairness_df):
        pass

class HiveDataStore(DataStore):
    """Hive data store implementation, which stores and retrieves fairness results in hive orc format"""

    def __init__(self, spark, data_source, data_table):
        super().__init__(spark, data_source, data_table)

    def is_supported(self):
        if self.data_source.type == "hive":
            return True

        return False

    def store_fairness_results(self, fairness_df):
        start_time = DateTimeUtil.current_milli_time()
        fairness_table = "{}.{}".format(self.data_table.db, self.data_table.table)
        self.logger.log_info("Storing fairness results in {}".format(fairness_table))
        fairness_df.write.mode("append").insertInto(fairness_table)
        #fairness_df.write.format("hive").mode("append").insertInto(fairness_table)
       
        
        self.logger.log_info("Completed storing fairness results in {} ms.".format(
            DateTimeUtil.current_milli_time()-start_time))


class JdbcDataStore(DataStore):
    """JDBC(DB2) data store implementation, which stores and retrieves fairness results"""

    def __init__(self, spark, data_source, data_table):
        super().__init__(spark, data_source, data_table)

    def is_supported(self):
        if self.data_source.type == "jdbc":
            return True

        return False

    def store_fairness_results(self, fairness_df):
        start_time = DateTimeUtil.current_milli_time()
        self.logger.log_info("Writing fairness results to {}.{} in db2".format(
            self.data_table.schema, self.data_table.table))
        
        fairness_df_col_names = fairness_df.columns
        probability_col = None
        gender_freqs_col = "gender_freqs"
        if gender_freqs_col in fairness_df_col_names:
            probability_col = gender_freqs_col

        DbUtils.write_dataframe_to_table(
            spark_df=fairness_df,
            location_type=self.data_source.location_type,
            database_name=self.data_table.db,
            schema_name=self.data_table.schema,
            table_name=self.data_table.table,
            connection_properties=self.data_source.jdbc_conn_props,
            probability_column = probability_col,
            spark=self.spark
        )
        end_time = DateTimeUtil.current_milli_time()
        self.logger.log_info("Completed writing fairness results to the table {}.{}".format(
            self.data_table.schema, self.data_table.table))
        self.logger.log_info(
            "Time taken to write the fairness results to db2 is {}".format(end_time-start_time))

