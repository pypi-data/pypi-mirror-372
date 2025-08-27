# ExperimentResultsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**summary** | [**ExperimentResultsSummaryCompact**](ExperimentResultsSummaryCompact.md) |  | 
**trays** | [**List[TrayResultsSummary]**](TrayResultsSummary.md) |  | 

## Example

```python
from spice_client.models.experiment_results_response import ExperimentResultsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExperimentResultsResponse from a JSON string
experiment_results_response_instance = ExperimentResultsResponse.from_json(json)
# print the JSON string representation of the object
print(ExperimentResultsResponse.to_json())

# convert the object into a dict
experiment_results_response_dict = experiment_results_response_instance.to_dict()
# create an instance of ExperimentResultsResponse from a dict
experiment_results_response_from_dict = ExperimentResultsResponse.from_dict(experiment_results_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


