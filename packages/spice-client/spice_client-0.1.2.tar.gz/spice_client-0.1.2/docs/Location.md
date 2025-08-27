# Location


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**area** | **object** |  | [optional] 
**color** | **str** |  | [optional] 
**comment** | **str** |  | [optional] 
**created_at** | **datetime** |  | 
**id** | **str** |  | 
**last_updated** | **datetime** |  | 
**name** | **str** |  | 
**project_id** | **str** |  | [optional] 
**project_name** | **str** |  | [optional] 

## Example

```python
from spice_client.models.location import Location

# TODO update the JSON string below
json = "{}"
# create an instance of Location from a JSON string
location_instance = Location.from_json(json)
# print the JSON string representation of the object
print(Location.to_json())

# convert the object into a dict
location_dict = location_instance.to_dict()
# create an instance of Location from a dict
location_from_dict = Location.from_dict(location_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


