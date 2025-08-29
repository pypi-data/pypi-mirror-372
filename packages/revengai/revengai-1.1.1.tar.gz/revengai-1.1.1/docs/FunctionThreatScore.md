# FunctionThreatScore


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**Dict[str, FunctionAnalysisThreatScoreData]**](FunctionAnalysisThreatScoreData.md) | The results of the function threat | 

## Example

```python
from revengai.models.function_threat_score import FunctionThreatScore

# TODO update the JSON string below
json = "{}"
# create an instance of FunctionThreatScore from a JSON string
function_threat_score_instance = FunctionThreatScore.from_json(json)
# print the JSON string representation of the object
print(FunctionThreatScore.to_json())

# convert the object into a dict
function_threat_score_dict = function_threat_score_instance.to_dict()
# create an instance of FunctionThreatScore from a dict
function_threat_score_from_dict = FunctionThreatScore.from_dict(function_threat_score_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


