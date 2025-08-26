# TemperatureDataWithProbes


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**average** | **str** |  | [optional] 
**experiment_id** | **str** |  | 
**id** | **str** |  | 
**image_filename** | **str** |  | [optional] 
**probe_readings** | [**List[ProbeTemperatureReadingWithMetadata]**](ProbeTemperatureReadingWithMetadata.md) |  | 
**timestamp** | **datetime** |  | 

## Example

```python
from spice_client.models.temperature_data_with_probes import TemperatureDataWithProbes

# TODO update the JSON string below
json = "{}"
# create an instance of TemperatureDataWithProbes from a JSON string
temperature_data_with_probes_instance = TemperatureDataWithProbes.from_json(json)
# print the JSON string representation of the object
print(TemperatureDataWithProbes.to_json())

# convert the object into a dict
temperature_data_with_probes_dict = temperature_data_with_probes_instance.to_dict()
# create an instance of TemperatureDataWithProbes from a dict
temperature_data_with_probes_from_dict = TemperatureDataWithProbes.from_dict(temperature_data_with_probes_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


