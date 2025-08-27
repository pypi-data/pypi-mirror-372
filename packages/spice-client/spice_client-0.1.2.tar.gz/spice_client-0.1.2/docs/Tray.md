# Tray


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**id** | **str** |  | 
**last_updated** | **datetime** |  | 
**lower_right_corner_x** | **int** |  | [optional] 
**lower_right_corner_y** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**order_sequence** | **int** |  | 
**probe_locations** | [**List[Probe]**](Probe.md) |  | 
**qty_cols** | **int** |  | [optional] 
**qty_rows** | **int** |  | [optional] 
**rotation_degrees** | **int** |  | 
**tray_configuration_id** | **str** |  | 
**upper_left_corner_x** | **int** |  | [optional] 
**upper_left_corner_y** | **int** |  | [optional] 
**well_relative_diameter** | **str** |  | [optional] 

## Example

```python
from spice_client.models.tray import Tray

# TODO update the JSON string below
json = "{}"
# create an instance of Tray from a JSON string
tray_instance = Tray.from_json(json)
# print the JSON string representation of the object
print(Tray.to_json())

# convert the object into a dict
tray_dict = tray_instance.to_dict()
# create an instance of Tray from a dict
tray_from_dict = Tray.from_dict(tray_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


