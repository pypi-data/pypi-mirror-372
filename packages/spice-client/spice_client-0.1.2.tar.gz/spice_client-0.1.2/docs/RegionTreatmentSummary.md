# RegionTreatmentSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enzyme_volume_litres** | **str** |  | [optional] 
**id** | **str** |  | 
**name** | **str** |  | 
**notes** | **str** |  | [optional] 
**sample** | [**Sample**](Sample.md) |  | [optional] 

## Example

```python
from spice_client.models.region_treatment_summary import RegionTreatmentSummary

# TODO update the JSON string below
json = "{}"
# create an instance of RegionTreatmentSummary from a JSON string
region_treatment_summary_instance = RegionTreatmentSummary.from_json(json)
# print the JSON string representation of the object
print(RegionTreatmentSummary.to_json())

# convert the object into a dict
region_treatment_summary_dict = region_treatment_summary_instance.to_dict()
# create an instance of RegionTreatmentSummary from a dict
region_treatment_summary_from_dict = RegionTreatmentSummary.from_dict(region_treatment_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


