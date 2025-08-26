# LocationCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** |  | [optional] 
**name** | **str** |  | 
**project_id** | **str** |  | [optional] 

## Example

```python
from spice_client.models.location_create import LocationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of LocationCreate from a JSON string
location_create_instance = LocationCreate.from_json(json)
# print the JSON string representation of the object
print(LocationCreate.to_json())

# convert the object into a dict
location_create_dict = location_create_instance.to_dict()
# create an instance of LocationCreate from a dict
location_create_from_dict = LocationCreate.from_dict(location_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


