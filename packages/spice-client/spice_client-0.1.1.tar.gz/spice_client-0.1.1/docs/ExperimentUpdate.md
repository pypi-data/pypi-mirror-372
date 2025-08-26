# ExperimentUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_calibration** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**performed_at** | **datetime** |  | [optional] 
**regions** | [**List[RegionUpdate]**](RegionUpdate.md) |  | [optional] 
**remarks** | **str** |  | [optional] 
**results** | [**ExperimentResultsResponse**](ExperimentResultsResponse.md) |  | [optional] 
**temperature_end** | **str** |  | [optional] 
**temperature_ramp** | **str** |  | [optional] 
**temperature_start** | **str** |  | [optional] 
**tray_configuration_id** | **str** |  | [optional] 
**username** | **str** |  | [optional] 

## Example

```python
from spice_client.models.experiment_update import ExperimentUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ExperimentUpdate from a JSON string
experiment_update_instance = ExperimentUpdate.from_json(json)
# print the JSON string representation of the object
print(ExperimentUpdate.to_json())

# convert the object into a dict
experiment_update_dict = experiment_update_instance.to_dict()
# create an instance of ExperimentUpdate from a dict
experiment_update_from_dict = ExperimentUpdate.from_dict(experiment_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


