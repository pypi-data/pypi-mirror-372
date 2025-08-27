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

try:
    from pyspark.sql.types import StructField, StructType, StringType, BinaryType, TimestampType
except ImportError as e:
    pass

from ibm_metrics_plugin.common.utils.metrics_logger import MetricLogger
from ibm_wos_utils.explainability.utils.date_time_util import DateTimeUtil
from ibm_wos_utils.joblib.utils.db_utils import DbUtils


class ExplanationsStore():
    """Class used to store explanations."""

    def __init__(self, spark, data_source, data_table):
        self.data_store = self.__get_data_store(
            spark=spark, data_source=data_source, data_table=data_table)

    def store_explanations(self, explanations):
        self.data_store.store_explanations(explanations)

    def get_explanations(self, percent):
        return self.data_store.get_explanations(percent=percent)

    def __get_data_store(self, spark, data_source, data_table):
        data_stores = [HiveDataStore(spark=spark, data_source=data_source, data_table=data_table), JdbcDataStore(
            spark=spark, data_source=data_source, data_table=data_table)]

        return next((d for d in data_stores if d.is_supported()), None)

    @staticmethod
    def get_explanations_schema():
        """Schema of the explanation rows stored"""
        fields = [StructField("created_at", TimestampType(), True),
                  StructField("explanation_type",
                              StringType(), True),
                  StructField("explanation", BinaryType(), True),
                  StructField("record_id", StringType(), False),
                  StructField("status", StringType(), True)]

        schema = StructType(fields)
        return StructType(sorted(schema, key=lambda f: f.name))


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
    def store_explanations(self, explanations):
        pass

    @abstractmethod
    def get_explanations(self, percent):
        pass


class HiveDataStore(DataStore):
    """Hive data store implementation, which stores and retrieves explanations in hive orc format"""

    def __init__(self, spark, data_source, data_table):
        super().__init__(spark, data_source, data_table)

    def is_supported(self):
        if self.data_source.type == "hive":
            return True

        return False

    def store_explanations(self, explanations_df):
        start_time = DateTimeUtil.current_milli_time()
        explanations_table = "{}.{}".format(
            self.data_table.db, self.data_table.table)
        self.logger.log_info(
            "Storing explanations in {}".format(explanations_table))
        explanations_df.write.mode("append").insertInto(explanations_table)
        self.logger.log_info("Completed storing explanations in {} ms.".format(
            DateTimeUtil.current_milli_time()-start_time))

    def get_explanations(self, percent):
        start_time = DateTimeUtil.current_milli_time()

        explanations_query = "SELECT {} FROM {}.{} TABLESAMPLE ({} PERCENT)".format(
            "explanation", self.data_table.db, self.data_table.table, percent)
        self.logger.log_info("Executing query {}.".format(explanations_query))
        explanations_df = self.spark.sql(explanations_query)
        explanations = explanations_df.collect()
        self.logger.log_info("Completed query execution in {} ms".format(
            DateTimeUtil.current_milli_time()-start_time))
        return self.__decode_explanations(explanations=explanations)

    def __decode_explanations(self, explanations):
        values = []
        for row in explanations:
            val = row["explanation"]
            if val and isinstance(val, bytearray):
                val = json.loads(base64.b64decode(val).decode("utf-8"))
            values.append(val)

        return values


class JdbcDataStore(DataStore):
    """JDBC(DB2) data store implementation, which stores and retrieves explanations"""

    def __init__(self, spark, data_source, data_table):
        super().__init__(spark, data_source, data_table)

    def is_supported(self):
        if self.data_source.type == "jdbc":
            return True

        return False

    def store_explanations(self, explanations_df):
        start_time = DateTimeUtil.current_milli_time()
        self.logger.log_info("Writing explanations data frame to {}.{} in db2".format(
            self.data_table.schema, self.data_table.table))
        DbUtils.write_dataframe_to_table(
            spark_df=explanations_df,
            location_type=self.data_source.location_type,
            database_name=self.data_table.db,
            schema_name=self.data_table.schema,
            table_name=self.data_table.table,
            connection_properties=self.data_source.jdbc_conn_props,
            spark=self.spark
        )
        end_time = DateTimeUtil.current_milli_time()
        self.logger.log_info("Completed writing explanations to the table {}.{}".format(
            self.data_table.schema, self.data_table.table))
        self.logger.log_info(
            "Time taken to write the explanations to db2 is {}".format(end_time-start_time))

    def get_explanations(self, percent):
        start_time = DateTimeUtil.current_milli_time()

        explanations_query = "SELECT \"{}\" FROM \"{}\".\"{}\" TABLESAMPLE BERNOULLI({}) REPEATABLE(5)".format(
            "explanation", self.data_table.schema, self.data_table.table, percent)
        self.logger.log_info("Executing query {}.".format(explanations_query))
        explanations_df = DbUtils.get_table_as_dataframe(spark=self.spark,
                                                         location_type=self.data_source.location_type,
                                                         database_name=self.data_table.db,
                                                         schema_name=self.data_table.schema,
                                                         table_name=self.data_table.table,
                                                         connection_properties=self.data_source.jdbc_conn_props,
                                                         sql_query=explanations_query)
        explanations = explanations_df.collect()
        self.logger.log_info("Completed query execution in {} ms".format(
            DateTimeUtil.current_milli_time()-start_time))
        return self.__decode_explanations(explanations=explanations)

    def __decode_explanations(self, explanations):
        values = []
        for row in explanations:
            val = row["explanation"]
            if val and isinstance(val, bytearray):
                val = json.loads(base64.b64decode(val).decode("utf-8"))
            values.append(val)

        return values
