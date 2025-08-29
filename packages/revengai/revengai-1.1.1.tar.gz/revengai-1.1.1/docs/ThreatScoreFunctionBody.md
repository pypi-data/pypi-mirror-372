# ThreatScoreFunctionBody


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**function_ids** | **List[int]** | List of function IDs to calculate threat score for | [optional] 

## Example

```python
from revengai.models.threat_score_function_body import ThreatScoreFunctionBody

# TODO update the JSON string below
json = "{}"
# create an instance of ThreatScoreFunctionBody from a JSON string
threat_score_function_body_instance = ThreatScoreFunctionBody.from_json(json)
# print the JSON string representation of the object
print(ThreatScoreFunctionBody.to_json())

# convert the object into a dict
threat_score_function_body_dict = threat_score_function_body_instance.to_dict()
# create an instance of ThreatScoreFunctionBody from a dict
threat_score_function_body_from_dict = ThreatScoreFunctionBody.from_dict(threat_score_function_body_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


