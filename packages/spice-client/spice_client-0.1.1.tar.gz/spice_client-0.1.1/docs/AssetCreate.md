# AssetCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**experiment_id** | **str** |  | [optional] 
**is_deleted** | **bool** |  | 
**original_filename** | **str** |  | 
**processing_message** | **str** |  | [optional] 
**processing_status** | **str** |  | [optional] 
**role** | **str** |  | [optional] 
**s3_key** | **str** |  | 
**size_bytes** | **int** |  | [optional] 
**type** | **str** |  | 
**uploaded_by** | **str** |  | [optional] 

## Example

```python
from spice_client.models.asset_create import AssetCreate

# TODO update the JSON string below
json = "{}"
# create an instance of AssetCreate from a JSON string
asset_create_instance = AssetCreate.from_json(json)
# print the JSON string representation of the object
print(AssetCreate.to_json())

# convert the object into a dict
asset_create_dict = asset_create_instance.to_dict()
# create an instance of AssetCreate from a dict
asset_create_from_dict = AssetCreate.from_dict(asset_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


