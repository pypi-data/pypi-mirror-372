# ExperimentList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**is_calibration** | **bool** |  | 
**last_updated** | **datetime** |  | 
**name** | **str** |  | 
**performed_at** | **datetime** |  | [optional] 
**username** | **str** |  | [optional] 

## Example

```python
from spice_client.models.experiment_list import ExperimentList

# TODO update the JSON string below
json = "{}"
# create an instance of ExperimentList from a JSON string
experiment_list_instance = ExperimentList.from_json(json)
# print the JSON string representation of the object
print(ExperimentList.to_json())

# convert the object into a dict
experiment_list_dict = experiment_list_instance.to_dict()
# create an instance of ExperimentList from a dict
experiment_list_from_dict = ExperimentList.from_dict(experiment_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


