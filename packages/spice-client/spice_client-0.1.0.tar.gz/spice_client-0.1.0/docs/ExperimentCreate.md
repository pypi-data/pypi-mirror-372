# ExperimentCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_calibration** | **bool** |  | 
**name** | **str** |  | 
**performed_at** | **datetime** |  | [optional] 
**regions** | [**List[RegionCreate]**](RegionCreate.md) |  | [optional] 
**remarks** | **str** |  | [optional] 
**results** | [**ExperimentResultsResponse**](ExperimentResultsResponse.md) |  | [optional] 
**temperature_end** | **str** |  | [optional] 
**temperature_ramp** | **str** |  | [optional] 
**temperature_start** | **str** |  | [optional] 
**tray_configuration_id** | **str** |  | [optional] 
**username** | **str** |  | [optional] 

## Example

```python
from spice_client.models.experiment_create import ExperimentCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ExperimentCreate from a JSON string
experiment_create_instance = ExperimentCreate.from_json(json)
# print the JSON string representation of the object
print(ExperimentCreate.to_json())

# convert the object into a dict
experiment_create_dict = experiment_create_instance.to_dict()
# create an instance of ExperimentCreate from a dict
experiment_create_from_dict = ExperimentCreate.from_dict(experiment_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


