# ProbeCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data_column_index** | **int** |  | 
**name** | **str** |  | 
**position_x** | **str** |  | 
**position_y** | **str** |  | 

## Example

```python
from spice_client.models.probe_create import ProbeCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ProbeCreate from a JSON string
probe_create_instance = ProbeCreate.from_json(json)
# print the JSON string representation of the object
print(ProbeCreate.to_json())

# convert the object into a dict
probe_create_dict = probe_create_instance.to_dict()
# create an instance of ProbeCreate from a dict
probe_create_from_dict = ProbeCreate.from_dict(probe_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


