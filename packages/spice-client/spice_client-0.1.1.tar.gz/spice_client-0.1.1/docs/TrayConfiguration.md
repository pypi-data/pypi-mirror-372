# TrayConfiguration


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**associated_experiments** | [**List[Experiment]**](Experiment.md) |  | 
**created_at** | **datetime** |  | 
**experiment_default** | **bool** |  | 
**id** | **str** |  | 
**last_updated** | **datetime** |  | 
**name** | **str** |  | [optional] 
**trays** | [**List[Tray]**](Tray.md) |  | 

## Example

```python
from spice_client.models.tray_configuration import TrayConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of TrayConfiguration from a JSON string
tray_configuration_instance = TrayConfiguration.from_json(json)
# print the JSON string representation of the object
print(TrayConfiguration.to_json())

# convert the object into a dict
tray_configuration_dict = tray_configuration_instance.to_dict()
# create an instance of TrayConfiguration from a dict
tray_configuration_from_dict = TrayConfiguration.from_dict(tray_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


