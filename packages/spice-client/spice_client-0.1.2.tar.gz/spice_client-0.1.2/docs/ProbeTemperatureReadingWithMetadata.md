# ProbeTemperatureReadingWithMetadata


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**id** | **str** |  | 
**probe_data_column_index** | **int** |  | 
**probe_id** | **str** |  | 
**probe_name** | **str** |  | 
**probe_position_x** | **str** |  | 
**probe_position_y** | **str** |  | 
**temperature** | **str** |  | 
**temperature_reading_id** | **str** |  | 

## Example

```python
from spice_client.models.probe_temperature_reading_with_metadata import ProbeTemperatureReadingWithMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of ProbeTemperatureReadingWithMetadata from a JSON string
probe_temperature_reading_with_metadata_instance = ProbeTemperatureReadingWithMetadata.from_json(json)
# print the JSON string representation of the object
print(ProbeTemperatureReadingWithMetadata.to_json())

# convert the object into a dict
probe_temperature_reading_with_metadata_dict = probe_temperature_reading_with_metadata_instance.to_dict()
# create an instance of ProbeTemperatureReadingWithMetadata from a dict
probe_temperature_reading_with_metadata_from_dict = ProbeTemperatureReadingWithMetadata.from_dict(probe_temperature_reading_with_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


