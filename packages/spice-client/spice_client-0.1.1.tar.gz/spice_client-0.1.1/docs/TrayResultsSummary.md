# TrayResultsSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tray_id** | **str** |  | 
**tray_name** | **str** |  | [optional] 
**wells** | [**List[TrayWellSummary]**](TrayWellSummary.md) |  | 

## Example

```python
from spice_client.models.tray_results_summary import TrayResultsSummary

# TODO update the JSON string below
json = "{}"
# create an instance of TrayResultsSummary from a JSON string
tray_results_summary_instance = TrayResultsSummary.from_json(json)
# print the JSON string representation of the object
print(TrayResultsSummary.to_json())

# convert the object into a dict
tray_results_summary_dict = tray_results_summary_instance.to_dict()
# create an instance of TrayResultsSummary from a dict
tray_results_summary_from_dict = TrayResultsSummary.from_dict(tray_results_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


