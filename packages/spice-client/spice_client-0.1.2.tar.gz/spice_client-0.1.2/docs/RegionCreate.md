# RegionCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**col_max** | **int** |  | [optional] 
**col_min** | **int** |  | [optional] 
**dilution_factor** | **int** |  | [optional] 
**display_colour_hex** | **str** |  | [optional] 
**is_background_key** | **bool** |  | 
**name** | **str** |  | [optional] 
**row_max** | **int** |  | [optional] 
**row_min** | **int** |  | [optional] 
**tray_id** | **int** |  | [optional] 
**treatment** | [**RegionTreatmentSummary**](RegionTreatmentSummary.md) |  | [optional] 
**treatment_id** | **str** |  | [optional] 

## Example

```python
from spice_client.models.region_create import RegionCreate

# TODO update the JSON string below
json = "{}"
# create an instance of RegionCreate from a JSON string
region_create_instance = RegionCreate.from_json(json)
# print the JSON string representation of the object
print(RegionCreate.to_json())

# convert the object into a dict
region_create_dict = region_create_instance.to_dict()
# create an instance of RegionCreate from a dict
region_create_from_dict = RegionCreate.from_dict(region_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


