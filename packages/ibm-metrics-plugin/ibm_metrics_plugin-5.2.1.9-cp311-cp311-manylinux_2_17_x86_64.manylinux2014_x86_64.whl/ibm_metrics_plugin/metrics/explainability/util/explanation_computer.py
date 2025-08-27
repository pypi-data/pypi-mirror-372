# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2021, 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import uuid
import base64
import json
import pandas as pd
try:
    from pyspark.sql import Row
except ImportError as e:
    pass
from more_itertools import ichunked
from ibm_metrics_plugin.common.utils.datetime_util import DateTimeUtil
DEFAULT_CHUNK_SIZE = 10000


class ExplanationComputer():

    def __init__(self, config, explainer, columns, accumulator, data_chunk_size=DEFAULT_CHUNK_SIZE, **kwargs):
        self.config = config
        self.explainer = explainer
        self.columns = columns
        self.accumulator = accumulator
        self.data_chunk_size = data_chunk_size
        self.kwargs = kwargs

    def compute(self, data):
        chunks = ichunked(data, self.data_chunk_size)
        for chunk in chunks:
            df = pd.DataFrame(chunk, columns=self.columns)
            response = self.explainer.explain(data=df, **self.kwargs)

            if self.accumulator:
                self.accumulator.add(
                    self.explainer.get_data_to_accumulate(response))

            if "local_explanations" in response:
                df["explanation"] = response.get("local_explanations")
                for _, row in df.iterrows():
                    yield self.get_response_row(row)

    def get_response_row(self, row):
        resp_row = Row(created_at=DateTimeUtil.get_current_datetime(),
                       explanation=self.__encode_explanation(
                           row["explanation"]),
                       explanation_type=self.config.metric_types[0].value,
                       record_id=row[self.config.record_id_column] if self.config.record_id_column else str(
                           uuid.uuid4()),
                       status="FINISHED")

        return resp_row

    def __encode_explanation(self, explanation):
        return bytearray(base64.b64encode(json.dumps(explanation).encode("utf-8")))
