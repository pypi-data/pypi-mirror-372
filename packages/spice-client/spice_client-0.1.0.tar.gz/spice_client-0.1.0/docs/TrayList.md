# TrayList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**lower_right_corner_x** | **int** |  | [optional] 
**lower_right_corner_y** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**order_sequence** | **int** |  | 
**probe_locations** | [**List[ProbeList]**](ProbeList.md) |  | 
**qty_cols** | **int** |  | [optional] 
**qty_rows** | **int** |  | [optional] 
**rotation_degrees** | **int** |  | 
**upper_left_corner_x** | **int** |  | [optional] 
**upper_left_corner_y** | **int** |  | [optional] 
**well_relative_diameter** | **str** |  | [optional] 

## Example

```python
from spice_client.models.tray_list import TrayList

# TODO update the JSON string below
json = "{}"
# create an instance of TrayList from a JSON string
tray_list_instance = TrayList.from_json(json)
# print the JSON string representation of the object
print(TrayList.to_json())

# convert the object into a dict
tray_list_dict = tray_list_instance.to_dict()
# create an instance of TrayList from a dict
tray_list_from_dict = TrayList.from_dict(tray_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


