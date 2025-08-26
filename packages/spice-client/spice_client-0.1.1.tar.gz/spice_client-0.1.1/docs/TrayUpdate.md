# TrayUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**lower_right_corner_x** | **int** |  | [optional] 
**lower_right_corner_y** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**order_sequence** | **int** |  | [optional] 
**probe_locations** | [**List[ProbeUpdate]**](ProbeUpdate.md) |  | [optional] 
**qty_cols** | **int** |  | [optional] 
**qty_rows** | **int** |  | [optional] 
**rotation_degrees** | **int** |  | [optional] 
**tray_configuration_id** | **str** |  | [optional] 
**upper_left_corner_x** | **int** |  | [optional] 
**upper_left_corner_y** | **int** |  | [optional] 
**well_relative_diameter** | **str** |  | [optional] 

## Example

```python
from spice_client.models.tray_update import TrayUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of TrayUpdate from a JSON string
tray_update_instance = TrayUpdate.from_json(json)
# print the JSON string representation of the object
print(TrayUpdate.to_json())

# convert the object into a dict
tray_update_dict = tray_update_instance.to_dict()
# create an instance of TrayUpdate from a dict
tray_update_from_dict = TrayUpdate.from_dict(tray_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


