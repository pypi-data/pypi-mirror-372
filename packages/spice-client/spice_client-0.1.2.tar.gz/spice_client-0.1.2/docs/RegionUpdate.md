# RegionUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**col_max** | **int** |  | [optional] 
**col_min** | **int** |  | [optional] 
**dilution_factor** | **int** |  | [optional] 
**display_colour_hex** | **str** |  | [optional] 
**experiment_id** | **str** |  | [optional] 
**is_background_key** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**row_max** | **int** |  | [optional] 
**row_min** | **int** |  | [optional] 
**tray_id** | **int** |  | [optional] 
**treatment** | [**RegionTreatmentSummary**](RegionTreatmentSummary.md) |  | [optional] 
**treatment_id** | **str** |  | [optional] 

## Example

```python
from spice_client.models.region_update import RegionUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RegionUpdate from a JSON string
region_update_instance = RegionUpdate.from_json(json)
# print the JSON string representation of the object
print(RegionUpdate.to_json())

# convert the object into a dict
region_update_dict = region_update_instance.to_dict()
# create an instance of RegionUpdate from a dict
region_update_from_dict = RegionUpdate.from_dict(region_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


