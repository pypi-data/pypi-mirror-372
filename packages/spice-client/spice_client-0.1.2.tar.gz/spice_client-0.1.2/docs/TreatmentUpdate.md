# TreatmentUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enzyme_volume_litres** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**name** | [**TreatmentName**](TreatmentName.md) |  | [optional] 
**notes** | **str** |  | [optional] 
**sample_id** | **str** |  | [optional] 

## Example

```python
from spice_client.models.treatment_update import TreatmentUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of TreatmentUpdate from a JSON string
treatment_update_instance = TreatmentUpdate.from_json(json)
# print the JSON string representation of the object
print(TreatmentUpdate.to_json())

# convert the object into a dict
treatment_update_dict = treatment_update_instance.to_dict()
# create an instance of TreatmentUpdate from a dict
treatment_update_from_dict = TreatmentUpdate.from_dict(treatment_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


