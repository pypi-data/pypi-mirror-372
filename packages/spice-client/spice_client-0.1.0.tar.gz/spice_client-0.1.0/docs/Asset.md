# Asset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**experiment_id** | **str** |  | [optional] 
**id** | **str** |  | 
**is_deleted** | **bool** |  | 
**last_updated** | **datetime** |  | 
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
from spice_client.models.asset import Asset

# TODO update the JSON string below
json = "{}"
# create an instance of Asset from a JSON string
asset_instance = Asset.from_json(json)
# print the JSON string representation of the object
print(Asset.to_json())

# convert the object into a dict
asset_dict = asset_instance.to_dict()
# create an instance of Asset from a dict
asset_from_dict = Asset.from_dict(asset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


