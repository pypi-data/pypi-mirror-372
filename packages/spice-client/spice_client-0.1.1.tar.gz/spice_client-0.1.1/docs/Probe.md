# Probe


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**data_column_index** | **int** |  | 
**id** | **str** |  | 
**last_updated** | **datetime** |  | 
**name** | **str** |  | 
**position_x** | **str** |  | 
**position_y** | **str** |  | 
**tray_id** | **str** |  | 

## Example

```python
from spice_client.models.probe import Probe

# TODO update the JSON string below
json = "{}"
# create an instance of Probe from a JSON string
probe_instance = Probe.from_json(json)
# print the JSON string representation of the object
print(Probe.to_json())

# convert the object into a dict
probe_dict = probe_instance.to_dict()
# create an instance of Probe from a dict
probe_from_dict = Probe.from_dict(probe_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


