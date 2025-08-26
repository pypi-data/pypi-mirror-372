# TrayConfigurationList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**experiment_default** | **bool** |  | 
**id** | **str** |  | 
**name** | **str** |  | [optional] 
**trays** | [**List[TrayList]**](TrayList.md) |  | 

## Example

```python
from spice_client.models.tray_configuration_list import TrayConfigurationList

# TODO update the JSON string below
json = "{}"
# create an instance of TrayConfigurationList from a JSON string
tray_configuration_list_instance = TrayConfigurationList.from_json(json)
# print the JSON string representation of the object
print(TrayConfigurationList.to_json())

# convert the object into a dict
tray_configuration_list_dict = tray_configuration_list_instance.to_dict()
# create an instance of TrayConfigurationList from a dict
tray_configuration_list_from_dict = TrayConfigurationList.from_dict(tray_configuration_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


