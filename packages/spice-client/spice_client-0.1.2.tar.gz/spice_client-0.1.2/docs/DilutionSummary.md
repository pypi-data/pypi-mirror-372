# DilutionSummary

Summary statistics grouped by dilution factor

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dilution_factor** | **int** | The dilution factor for this group | 
**statistics** | [**NucleationStatistics**](NucleationStatistics.md) | Statistics for wells at this dilution level | 

## Example

```python
from spice_client.models.dilution_summary import DilutionSummary

# TODO update the JSON string below
json = "{}"
# create an instance of DilutionSummary from a JSON string
dilution_summary_instance = DilutionSummary.from_json(json)
# print the JSON string representation of the object
print(DilutionSummary.to_json())

# convert the object into a dict
dilution_summary_dict = dilution_summary_instance.to_dict()
# create an instance of DilutionSummary from a dict
dilution_summary_from_dict = DilutionSummary.from_dict(dilution_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


