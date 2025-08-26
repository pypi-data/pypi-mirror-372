# Sample


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**air_volume_litres** | **str** |  | [optional] 
**created_at** | **datetime** |  | 
**extraction_procedure** | **str** |  | [optional] 
**filter_substrate** | **str** |  | [optional] 
**flow_litres_per_minute** | **str** |  | [optional] 
**id** | **str** |  | 
**initial_concentration_gram_l** | **str** |  | [optional] 
**last_updated** | **datetime** |  | 
**latitude** | **str** |  | [optional] 
**location** | [**Location**](Location.md) |  | [optional] 
**location_id** | **str** |  | [optional] 
**longitude** | **str** |  | [optional] 
**material_description** | **str** |  | [optional] 
**name** | **str** |  | 
**remarks** | **str** |  | [optional] 
**start_time** | **datetime** |  | [optional] 
**stop_time** | **datetime** |  | [optional] 
**suspension_volume_litres** | **str** |  | [optional] 
**total_volume** | **str** |  | [optional] 
**treatments** | [**List[Treatment]**](Treatment.md) |  | 
**type** | [**SampleType**](SampleType.md) |  | 
**water_volume_litres** | **str** |  | [optional] 
**well_volume_litres** | **str** |  | [optional] 

## Example

```python
from spice_client.models.sample import Sample

# TODO update the JSON string below
json = "{}"
# create an instance of Sample from a JSON string
sample_instance = Sample.from_json(json)
# print the JSON string representation of the object
print(Sample.to_json())

# convert the object into a dict
sample_dict = sample_instance.to_dict()
# create an instance of Sample from a dict
sample_from_dict = Sample.from_dict(sample_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


