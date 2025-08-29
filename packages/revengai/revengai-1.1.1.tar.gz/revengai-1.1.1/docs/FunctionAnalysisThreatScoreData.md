# FunctionAnalysisThreatScoreData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**min** | **float** | The minimum value for the analysis score | 
**max** | **float** | The maximum value for the analysis score | 
**average** | **float** | The average value for the analysis score | 
**upper** | **float** | The upper limit for the analysis score | 
**lower** | **float** | The lower limit for the analysis score | 
**malware_count** | **int** | Number of malware binaries used in threat score calculation | 
**benign_count** | **int** | Number of benign binaries used in threat score calculation | 

## Example

```python
from revengai.models.function_analysis_threat_score_data import FunctionAnalysisThreatScoreData

# TODO update the JSON string below
json = "{}"
# create an instance of FunctionAnalysisThreatScoreData from a JSON string
function_analysis_threat_score_data_instance = FunctionAnalysisThreatScoreData.from_json(json)
# print the JSON string representation of the object
print(FunctionAnalysisThreatScoreData.to_json())

# convert the object into a dict
function_analysis_threat_score_data_dict = function_analysis_threat_score_data_instance.to_dict()
# create an instance of FunctionAnalysisThreatScoreData from a dict
function_analysis_threat_score_data_from_dict = FunctionAnalysisThreatScoreData.from_dict(function_analysis_threat_score_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


