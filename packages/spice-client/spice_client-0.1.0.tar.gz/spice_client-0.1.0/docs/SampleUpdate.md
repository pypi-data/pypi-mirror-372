# SampleUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**air_volume_litres** | **str** |  | [optional] 
**extraction_procedure** | **str** |  | [optional] 
**filter_substrate** | **str** |  | [optional] 
**flow_litres_per_minute** | **str** |  | [optional] 
**initial_concentration_gram_l** | **str** |  | [optional] 
**latitude** | **str** |  | [optional] 
**location** | [**Location**](Location.md) |  | [optional] 
**location_id** | **str** |  | [optional] 
**longitude** | **str** |  | [optional] 
**material_description** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**remarks** | **str** |  | [optional] 
**start_time** | **datetime** |  | [optional] 
**stop_time** | **datetime** |  | [optional] 
**suspension_volume_litres** | **str** |  | [optional] 
**total_volume** | **str** |  | [optional] 
**treatments** | [**List[TreatmentUpdate]**](TreatmentUpdate.md) |  | [optional] 
**type** | [**SampleType**](SampleType.md) |  | [optional] 
**water_volume_litres** | **str** |  | [optional] 
**well_volume_litres** | **str** |  | [optional] 

## Example

```python
from spice_client.models.sample_update import SampleUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of SampleUpdate from a JSON string
sample_update_instance = SampleUpdate.from_json(json)
# print the JSON string representation of the object
print(SampleUpdate.to_json())

# convert the object into a dict
sample_update_dict = sample_update_instance.to_dict()
# create an instance of SampleUpdate from a dict
sample_update_from_dict = SampleUpdate.from_dict(sample_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


