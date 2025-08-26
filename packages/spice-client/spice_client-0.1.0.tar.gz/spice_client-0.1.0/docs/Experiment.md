# Experiment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**id** | **str** |  | 
**is_calibration** | **bool** |  | 
**last_updated** | **datetime** |  | 
**name** | **str** |  | 
**performed_at** | **datetime** |  | [optional] 
**regions** | [**List[Region]**](Region.md) |  | 
**remarks** | **str** |  | [optional] 
**results** | [**ExperimentResultsResponse**](ExperimentResultsResponse.md) |  | [optional] 
**temperature_end** | **str** |  | [optional] 
**temperature_ramp** | **str** |  | [optional] 
**temperature_start** | **str** |  | [optional] 
**tray_configuration_id** | **str** |  | [optional] 
**username** | **str** |  | [optional] 

## Example

```python
from spice_client.models.experiment import Experiment

# TODO update the JSON string below
json = "{}"
# create an instance of Experiment from a JSON string
experiment_instance = Experiment.from_json(json)
# print the JSON string representation of the object
print(Experiment.to_json())

# convert the object into a dict
experiment_dict = experiment_instance.to_dict()
# create an instance of Experiment from a dict
experiment_from_dict = Experiment.from_dict(experiment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


