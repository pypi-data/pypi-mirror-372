# BaseResponseFunctionAnalysisThreatScoreData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **bool** | Response status on whether the request succeeded | [optional] [default to True]
**data** | [**FunctionAnalysisThreatScoreData**](FunctionAnalysisThreatScoreData.md) |  | [optional] 
**message** | **str** |  | [optional] 
**errors** | [**List[ErrorModel]**](ErrorModel.md) |  | [optional] 
**meta** | [**MetaModel**](MetaModel.md) | Metadata | [optional] 

## Example

```python
from revengai.models.base_response_function_analysis_threat_score_data import BaseResponseFunctionAnalysisThreatScoreData

# TODO update the JSON string below
json = "{}"
# create an instance of BaseResponseFunctionAnalysisThreatScoreData from a JSON string
base_response_function_analysis_threat_score_data_instance = BaseResponseFunctionAnalysisThreatScoreData.from_json(json)
# print the JSON string representation of the object
print(BaseResponseFunctionAnalysisThreatScoreData.to_json())

# convert the object into a dict
base_response_function_analysis_threat_score_data_dict = base_response_function_analysis_threat_score_data_instance.to_dict()
# create an instance of BaseResponseFunctionAnalysisThreatScoreData from a dict
base_response_function_analysis_threat_score_data_from_dict = BaseResponseFunctionAnalysisThreatScoreData.from_dict(base_response_function_analysis_threat_score_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


