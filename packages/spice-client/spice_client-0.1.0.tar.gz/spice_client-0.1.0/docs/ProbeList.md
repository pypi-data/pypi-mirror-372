# ProbeList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data_column_index** | **int** |  | 
**id** | **str** |  | 
**name** | **str** |  | 
**position_x** | **str** |  | 
**position_y** | **str** |  | 

## Example

```python
from spice_client.models.probe_list import ProbeList

# TODO update the JSON string below
json = "{}"
# create an instance of ProbeList from a JSON string
probe_list_instance = ProbeList.from_json(json)
# print the JSON string representation of the object
print(ProbeList.to_json())

# convert the object into a dict
probe_list_dict = probe_list_instance.to_dict()
# create an instance of ProbeList from a dict
probe_list_from_dict = ProbeList.from_dict(probe_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


