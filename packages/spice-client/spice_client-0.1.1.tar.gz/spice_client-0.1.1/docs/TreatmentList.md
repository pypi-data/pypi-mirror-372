# TreatmentList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enzyme_volume_litres** | **str** |  | [optional] 
**id** | **str** |  | 
**name** | [**TreatmentName**](TreatmentName.md) |  | 
**notes** | **str** |  | [optional] 

## Example

```python
from spice_client.models.treatment_list import TreatmentList

# TODO update the JSON string below
json = "{}"
# create an instance of TreatmentList from a JSON string
treatment_list_instance = TreatmentList.from_json(json)
# print the JSON string representation of the object
print(TreatmentList.to_json())

# convert the object into a dict
treatment_list_dict = treatment_list_instance.to_dict()
# create an instance of TreatmentList from a dict
treatment_list_from_dict = TreatmentList.from_dict(treatment_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


