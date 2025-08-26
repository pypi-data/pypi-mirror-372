# LocationUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **str** |  | [optional] 

## Example

```python
from spice_client.models.location_update import LocationUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of LocationUpdate from a JSON string
location_update_instance = LocationUpdate.from_json(json)
# print the JSON string representation of the object
print(LocationUpdate.to_json())

# convert the object into a dict
location_update_dict = location_update_instance.to_dict()
# create an instance of LocationUpdate from a dict
location_update_from_dict = LocationUpdate.from_dict(location_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


