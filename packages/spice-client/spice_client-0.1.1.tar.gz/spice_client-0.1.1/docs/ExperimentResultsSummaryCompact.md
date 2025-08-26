# ExperimentResultsSummaryCompact


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_timestamp** | **datetime** |  | [optional] 
**last_timestamp** | **datetime** |  | [optional] 
**total_time_points** | **int** |  | 

## Example

```python
from spice_client.models.experiment_results_summary_compact import ExperimentResultsSummaryCompact

# TODO update the JSON string below
json = "{}"
# create an instance of ExperimentResultsSummaryCompact from a JSON string
experiment_results_summary_compact_instance = ExperimentResultsSummaryCompact.from_json(json)
# print the JSON string representation of the object
print(ExperimentResultsSummaryCompact.to_json())

# convert the object into a dict
experiment_results_summary_compact_dict = experiment_results_summary_compact_instance.to_dict()
# create an instance of ExperimentResultsSummaryCompact from a dict
experiment_results_summary_compact_from_dict = ExperimentResultsSummaryCompact.from_dict(experiment_results_summary_compact_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


