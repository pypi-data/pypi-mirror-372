# Region


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**col_max** | **int** |  | [optional] 
**col_min** | **int** |  | [optional] 
**created_at** | **datetime** |  | 
**dilution_factor** | **int** |  | [optional] 
**display_colour_hex** | **str** |  | [optional] 
**experiment_id** | **str** |  | 
**id** | **str** |  | 
**is_background_key** | **bool** |  | 
**last_updated** | **datetime** |  | 
**name** | **str** |  | [optional] 
**row_max** | **int** |  | [optional] 
**row_min** | **int** |  | [optional] 
**tray_id** | **int** |  | [optional] 
**treatment** | [**RegionTreatmentSummary**](RegionTreatmentSummary.md) |  | [optional] 
**treatment_id** | **str** |  | [optional] 

## Example

```python
from spice_client.models.region import Region

# TODO update the JSON string below
json = "{}"
# create an instance of Region from a JSON string
region_instance = Region.from_json(json)
# print the JSON string representation of the object
print(Region.to_json())

# convert the object into a dict
region_dict = region_instance.to_dict()
# create an instance of Region from a dict
region_from_dict = Region.from_dict(region_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


