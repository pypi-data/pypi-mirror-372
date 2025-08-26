# TrayCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**lower_right_corner_x** | **int** |  | [optional] 
**lower_right_corner_y** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**order_sequence** | **int** |  | 
**probe_locations** | [**List[ProbeCreate]**](ProbeCreate.md) |  | [optional] 
**qty_cols** | **int** |  | [optional] 
**qty_rows** | **int** |  | [optional] 
**rotation_degrees** | **int** |  | 
**upper_left_corner_x** | **int** |  | [optional] 
**upper_left_corner_y** | **int** |  | [optional] 
**well_relative_diameter** | **str** |  | [optional] 

## Example

```python
from spice_client.models.tray_create import TrayCreate

# TODO update the JSON string below
json = "{}"
# create an instance of TrayCreate from a JSON string
tray_create_instance = TrayCreate.from_json(json)
# print the JSON string representation of the object
print(TrayCreate.to_json())

# convert the object into a dict
tray_create_dict = tray_create_instance.to_dict()
# create an instance of TrayCreate from a dict
tray_create_from_dict = TrayCreate.from_dict(tray_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


