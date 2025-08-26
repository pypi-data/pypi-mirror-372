# TrayConfigurationUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**associated_experiments** | [**List[Experiment]**](Experiment.md) |  | [optional] 
**experiment_default** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**trays** | [**List[TrayUpdate]**](TrayUpdate.md) |  | [optional] 

## Example

```python
from spice_client.models.tray_configuration_update import TrayConfigurationUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of TrayConfigurationUpdate from a JSON string
tray_configuration_update_instance = TrayConfigurationUpdate.from_json(json)
# print the JSON string representation of the object
print(TrayConfigurationUpdate.to_json())

# convert the object into a dict
tray_configuration_update_dict = tray_configuration_update_instance.to_dict()
# create an instance of TrayConfigurationUpdate from a dict
tray_configuration_update_from_dict = TrayConfigurationUpdate.from_dict(tray_configuration_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


