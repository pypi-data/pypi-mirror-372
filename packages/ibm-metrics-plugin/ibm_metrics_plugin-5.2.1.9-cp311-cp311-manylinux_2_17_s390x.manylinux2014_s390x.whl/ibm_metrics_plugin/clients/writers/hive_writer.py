# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2021, 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

class HiveWriter:

    def __init__(self, credentials) -> None:
        self.credentials = credentials

    def write(self, data) -> None:
        print(data)
        #TODO: Implement hive writer

