# ProbeUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data_column_index** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**position_x** | **str** |  | [optional] 
**position_y** | **str** |  | [optional] 
**tray_id** | **str** |  | [optional] 

## Example

```python
from spice_client.models.probe_update import ProbeUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ProbeUpdate from a JSON string
probe_update_instance = ProbeUpdate.from_json(json)
# print the JSON string representation of the object
print(ProbeUpdate.to_json())

# convert the object into a dict
probe_update_dict = probe_update_instance.to_dict()
# create an instance of ProbeUpdate from a dict
probe_update_from_dict = ProbeUpdate.from_dict(probe_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


