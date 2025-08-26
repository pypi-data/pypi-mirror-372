# TreatmentCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enzyme_volume_litres** | **str** |  | [optional] 
**name** | [**TreatmentName**](TreatmentName.md) |  | 
**notes** | **str** |  | [optional] 
**sample_id** | **str** |  | [optional] 

## Example

```python
from spice_client.models.treatment_create import TreatmentCreate

# TODO update the JSON string below
json = "{}"
# create an instance of TreatmentCreate from a JSON string
treatment_create_instance = TreatmentCreate.from_json(json)
# print the JSON string representation of the object
print(TreatmentCreate.to_json())

# convert the object into a dict
treatment_create_dict = treatment_create_instance.to_dict()
# create an instance of TreatmentCreate from a dict
treatment_create_from_dict = TreatmentCreate.from_dict(treatment_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


