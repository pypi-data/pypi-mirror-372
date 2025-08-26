# Treatment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** |  | 
**dilution_summaries** | [**List[DilutionSummary]**](DilutionSummary.md) |  | 
**enzyme_volume_litres** | **str** |  | [optional] 
**experimental_results** | [**List[NucleationEvent]**](NucleationEvent.md) |  | 
**id** | **str** |  | 
**last_updated** | **datetime** |  | 
**name** | [**TreatmentName**](TreatmentName.md) |  | 
**notes** | **str** |  | [optional] 
**sample_id** | **str** |  | [optional] 
**statistics** | [**NucleationStatistics**](NucleationStatistics.md) |  | [optional] 

## Example

```python
from spice_client.models.treatment import Treatment

# TODO update the JSON string below
json = "{}"
# create an instance of Treatment from a JSON string
treatment_instance = Treatment.from_json(json)
# print the JSON string representation of the object
print(Treatment.to_json())

# convert the object into a dict
treatment_dict = treatment_instance.to_dict()
# create an instance of Treatment from a dict
treatment_from_dict = Treatment.from_dict(treatment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


