# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2021, 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from .hive_writer import HiveWriter
from .jdbc_writer import JdbcWriter

def get_writer(credentials):
    """
    Returns a writer object based on the credentials provided.
    """
    if credentials["type"] == "jdbc":
        return JdbcWriter(credentials)
    elif credentials["type"] == "hive":
        return HiveWriter(credentials)
    else:
        raise ValueError("Unknown writer type: {}".format(credentials["type"]))