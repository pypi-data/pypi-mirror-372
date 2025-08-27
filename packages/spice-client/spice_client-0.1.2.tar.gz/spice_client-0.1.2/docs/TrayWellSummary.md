# TrayWellSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column_number** | **int** |  | 
**coordinate** | **str** |  | 
**dilution_factor** | **int** |  | [optional] 
**first_phase_change_time** | **datetime** |  | [optional] 
**image_asset_id** | **str** |  | [optional] 
**row_letter** | **str** |  | 
**sample** | [**Sample**](Sample.md) |  | [optional] 
**temperatures** | [**TemperatureDataWithProbes**](TemperatureDataWithProbes.md) |  | [optional] 
**total_phase_changes** | **int** |  | 
**treatment** | [**Treatment**](Treatment.md) |  | [optional] 

## Example

```python
from spice_client.models.tray_well_summary import TrayWellSummary

# TODO update the JSON string below
json = "{}"
# create an instance of TrayWellSummary from a JSON string
tray_well_summary_instance = TrayWellSummary.from_json(json)
# print the JSON string representation of the object
print(TrayWellSummary.to_json())

# convert the object into a dict
tray_well_summary_dict = tray_well_summary_instance.to_dict()
# create an instance of TrayWellSummary from a dict
tray_well_summary_from_dict = TrayWellSummary.from_dict(tray_well_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


