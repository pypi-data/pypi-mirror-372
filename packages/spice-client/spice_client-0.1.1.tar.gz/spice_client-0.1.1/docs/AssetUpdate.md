# AssetUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**experiment_id** | **str** |  | [optional] 
**is_deleted** | **bool** |  | [optional] 
**original_filename** | **str** |  | [optional] 
**processing_message** | **str** |  | [optional] 
**processing_status** | **str** |  | [optional] 
**role** | **str** |  | [optional] 
**s3_key** | **str** |  | [optional] 
**size_bytes** | **int** |  | [optional] 
**type** | **str** |  | [optional] 
**uploaded_at** | **datetime** |  | [optional] 
**uploaded_by** | **str** |  | [optional] 

## Example

```python
from spice_client.models.asset_update import AssetUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of AssetUpdate from a JSON string
asset_update_instance = AssetUpdate.from_json(json)
# print the JSON string representation of the object
print(AssetUpdate.to_json())

# convert the object into a dict
asset_update_dict = asset_update_instance.to_dict()
# create an instance of AssetUpdate from a dict
asset_update_from_dict = AssetUpdate.from_dict(asset_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


