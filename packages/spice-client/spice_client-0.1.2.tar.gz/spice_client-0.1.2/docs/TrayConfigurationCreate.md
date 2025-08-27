# TrayConfigurationCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**experiment_default** | **bool** |  | 
**name** | **str** |  | [optional] 
**trays** | [**List[TrayCreate]**](TrayCreate.md) |  | [optional] 

## Example

```python
from spice_client.models.tray_configuration_create import TrayConfigurationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of TrayConfigurationCreate from a JSON string
tray_configuration_create_instance = TrayConfigurationCreate.from_json(json)
# print the JSON string representation of the object
print(TrayConfigurationCreate.to_json())

# convert the object into a dict
tray_configuration_create_dict = tray_configuration_create_instance.to_dict()
# create an instance of TrayConfigurationCreate from a dict
tray_configuration_create_from_dict = TrayConfigurationCreate.from_dict(tray_configuration_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


