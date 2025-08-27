
#----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2023  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import datasets
import evaluate

import pandas as pd

try:
    from unitxt.metrics import Metric,NER
    from unitxt.stream import MultiStream   
    from unitxt.artifact import fetch_artifact
    from unitxt.artifact import Artifact     
except ImportError as e:
    msg = "Please install unitxt package to extract entities"
    print(msg)
    


_CITATION = "citation"
_DESCRIPTION = "description"
_KWARGS_DESCRIPTION = "description"

@evaluate.utils.file_utils.add_start_docstrings(_DESCRIPTION, _KWARGS_DESCRIPTION)
class NERImplementation(evaluate.Metric):
    def _info(self):

        return evaluate.MetricInfo(
            description=_DESCRIPTION,
            citation=_CITATION,
            homepage="homepage",
            inputs_description=_KWARGS_DESCRIPTION,
            features=datasets.Features(
                datasets.Features(
                    {
                        "predictions": datasets.Value("string", id="sequence"),
                        "references": datasets.Value("string", id="sequence"),
                    }
                )
            )
        )

    def _download_and_prepare(self, dl_manager):
        pass
        
    def _compute(self, predictions, references):
        
        metric = NER()
        multi_stream = self.__create_stream(predictions,references)
        multi_stream = self.__run_postprocessor("processors.to_span_label_pairs",multi_stream)
        results = self.__apply_metric(metric,multi_stream)
        summary_metrics = self.__get_global_entity_extraction_metrics(results)
        individual_metrics = self.__get_individual_record_metrics(results)
        return summary_metrics, individual_metrics
    
    def __switch_tuples_in_list(self, alist):
        new_list = [ (atuple[1],atuple[0]) for atuple in alist ]
        return new_list
    
    def __create_stream(self,  predictions: list[str], references: list[list[str]]):
        test_iterable = [
            {"prediction": prediction, "references": [reference]} for prediction, reference in zip(predictions, references)
        ]
        multi_stream = MultiStream.from_iterables({"test": test_iterable}, copying=True)
        return multi_stream
    
    def __run_postprocessor(self, post_processor: str, multi_stream: MultiStream):
        post_processor , _ = fetch_artifact(post_processor)
        output_multi_stream = post_processor.process(multi_stream)
        #print(output_multi_stream.to_dataset()["test"][0])
        return output_multi_stream    
        
    def __apply_metric(self, metric: Metric, multi_stream):
        output_multi_stream = metric(multi_stream)
        output_stream = output_multi_stream["test"]
        return list(output_stream)

    
    def __get_global_entity_extraction_metrics(self, results):
    
        f1_micro = results[0]['score']['global']['f1_micro']
        f1_macro = results[0]['score']['global']['f1_macro']
        precision_micro = results[0]['score']['global']['precision_micro']
        precision_macro = results[0]['score']['global']['precision_macro']
        recall_micro = results[0]['score']['global']['recall_micro']
        recall_macro = results[0]['score']['global']['recall_macro']
    
        aggregated_metrics = {}
        aggregated_metrics['micro_f1'] = { "metric_value":round(f1_micro, 4)}
        aggregated_metrics['macro_f1'] = { "metric_value":round(f1_macro, 4)}
        aggregated_metrics['micro_precision'] = { "metric_value":round(precision_micro, 4)}
        aggregated_metrics['macro_precision'] = { "metric_value":round(precision_macro, 4)}
        aggregated_metrics['micro_recall'] = { "metric_value":round(recall_micro, 4)}
        aggregated_metrics['macro_recall'] = { "metric_value":round(recall_macro, 4)}
        
        
        return aggregated_metrics
    
    def __get_individual_record_metrics(self, results):
        values = []
        for result in results:
            value = []
            
            instance = result['score']['instance']
            if (len(result['prediction']) == 0):
                f1_micro = 0
                f1_macro = 0
                precision_micro = 0 
                precision_macro = 0
                recall_micro = 0
                recall_macro = 0
            else:
                f1_micro = round(instance['f1_micro'], 4)
                f1_macro = round(instance['f1_macro'], 4)
                precision_micro = round(instance['precision_micro'], 4)
                precision_macro = round(instance['precision_macro'], 4)
                recall_micro = round(instance['recall_micro'], 4)
                recall_macro = round(instance['recall_macro'], 4)
    
            value.append(f1_micro)
            value.append(f1_macro)
            value.append(precision_micro)
            value.append(precision_macro)
            value.append(recall_micro)
            value.append(recall_macro)
    
            values.append(value)
        columns = ['micro_f1', 'macro_f1', 'micro_precision', 'macro_precision', 'micro_recall', 'macro_recall']
        
        return pd.DataFrame(values, columns = columns)        
    
              
        