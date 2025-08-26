# NucleationStatistics

Summary statistics for nucleation events, used for sample and treatment analysis

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**frozen_count** | **int** | Number of wells that nucleated (froze) | 
**liquid_count** | **int** | Number of wells that remained liquid | 
**mean_nucleation_temp_celsius** | **float** | Mean nucleation temperature in Celsius for wells that froze | [optional] 
**median_nucleation_time_seconds** | **int** | Median nucleation time in seconds for wells that froze | [optional] 
**success_rate** | **float** | Success rate as a fraction (0.0 to 1.0) | 
**total_wells** | **int** | Total number of wells tested | 

## Example

```python
from spice_client.models.nucleation_statistics import NucleationStatistics

# TODO update the JSON string below
json = "{}"
# create an instance of NucleationStatistics from a JSON string
nucleation_statistics_instance = NucleationStatistics.from_json(json)
# print the JSON string representation of the object
print(NucleationStatistics.to_json())

# convert the object into a dict
nucleation_statistics_dict = nucleation_statistics_instance.to_dict()
# create an instance of NucleationStatistics from a dict
nucleation_statistics_from_dict = NucleationStatistics.from_dict(nucleation_statistics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


