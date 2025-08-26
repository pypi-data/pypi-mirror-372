# LocationList


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
from spice_client.models.location_list import LocationList

# TODO update the JSON string below
json = "{}"
# create an instance of LocationList from a JSON string
location_list_instance = LocationList.from_json(json)
# print the JSON string representation of the object
print(LocationList.to_json())

# convert the object into a dict
location_list_dict = location_list_instance.to_dict()
# create an instance of LocationList from a dict
location_list_from_dict = LocationList.from_dict(location_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


