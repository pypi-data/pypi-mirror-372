# NucleationEvent

Shared struct for nucleation events across experiments, samples, and treatments Represents the scientific result of ice nucleation for a single well Uses scientific naming conventions with explicit units

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dilution_factor** | **int** | Dilution factor applied to the sample in this well | [optional] 
**experiment_date** | **datetime** | Date and time when the experiment was performed | [optional] 
**experiment_id** | **str** | Unique identifier for the experiment this event occurred in | 
**experiment_name** | **str** | Human-readable name of the experiment | 
**final_state** | **str** | Final state of the well: \&quot;frozen\&quot;, \&quot;liquid\&quot;, or \&quot;&#x60;no_data&#x60;\&quot; | 
**freezing_temperature_avg** | **str** | UI compatibility field - same as &#x60;nucleation_temperature_avg_celsius&#x60; | [optional] 
**freezing_time_seconds** | **int** | UI compatibility field - same as &#x60;nucleation_time_seconds&#x60; | [optional] 
**nucleation_temperature_avg_celsius** | **str** | Average temperature across all temperature probes at nucleation event, in Celsius | [optional] 
**nucleation_time_seconds** | **int** | Time from experiment start to nucleation in seconds | [optional] 
**tray_name** | **str** | Name of the tray/plate (e.g., \&quot;P1\&quot;, \&quot;P2\&quot;) | [optional] 
**treatment_id** | **str** | ID of the treatment applied to this sample | [optional] 
**treatment_name** | **str** | Name of the treatment applied to this sample | [optional] 
**well_coordinate** | **str** | Well coordinate in standard format (e.g., \&quot;A1\&quot;, \&quot;B2\&quot;, \&quot;H12\&quot;) | 

## Example

```python
from spice_client.models.nucleation_event import NucleationEvent

# TODO update the JSON string below
json = "{}"
# create an instance of NucleationEvent from a JSON string
nucleation_event_instance = NucleationEvent.from_json(json)
# print the JSON string representation of the object
print(NucleationEvent.to_json())

# convert the object into a dict
nucleation_event_dict = nucleation_event_instance.to_dict()
# create an instance of NucleationEvent from a dict
nucleation_event_from_dict = NucleationEvent.from_dict(nucleation_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


