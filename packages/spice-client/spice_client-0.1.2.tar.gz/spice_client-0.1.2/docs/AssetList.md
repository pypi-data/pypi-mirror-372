# AssetList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**experiment_id** | **str** |  | [optional] 
**id** | **str** |  | 
**is_deleted** | **bool** |  | 
**original_filename** | **str** |  | 
**processing_message** | **str** |  | [optional] 
**processing_status** | **str** |  | [optional] 
**role** | **str** |  | [optional] 
**s3_key** | **str** |  | 
**size_bytes** | **int** |  | [optional] 
**type** | **str** |  | 
**uploaded_at** | **datetime** |  | 
**uploaded_by** | **str** |  | [optional] 

## Example

```python
from spice_client.models.asset_list import AssetList

# TODO update the JSON string below
json = "{}"
# create an instance of AssetList from a JSON string
asset_list_instance = AssetList.from_json(json)
# print the JSON string representation of the object
print(AssetList.to_json())

# convert the object into a dict
asset_list_dict = asset_list_instance.to_dict()
# create an instance of AssetList from a dict
asset_list_from_dict = AssetList.from_dict(asset_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


