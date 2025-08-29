# AppCoreResponsesBaseBaseResponseAnalysisTags2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **bool** | Response status on whether the request succeeded | [optional] [default to True]
**data** | [**AppApiRestV2AnalysesResponsesAnalysisTags**](AppApiRestV2AnalysesResponsesAnalysisTags.md) |  | [optional] 
**message** | **str** |  | [optional] 
**errors** | [**List[ErrorModel]**](ErrorModel.md) |  | [optional] 
**meta** | [**MetaModel**](MetaModel.md) | Metadata | [optional] 

## Example

```python
from revengai.models.app_core_responses_base_base_response_analysis_tags2 import AppCoreResponsesBaseBaseResponseAnalysisTags2

# TODO update the JSON string below
json = "{}"
# create an instance of AppCoreResponsesBaseBaseResponseAnalysisTags2 from a JSON string
app_core_responses_base_base_response_analysis_tags2_instance = AppCoreResponsesBaseBaseResponseAnalysisTags2.from_json(json)
# print the JSON string representation of the object
print(AppCoreResponsesBaseBaseResponseAnalysisTags2.to_json())

# convert the object into a dict
app_core_responses_base_base_response_analysis_tags2_dict = app_core_responses_base_base_response_analysis_tags2_instance.to_dict()
# create an instance of AppCoreResponsesBaseBaseResponseAnalysisTags2 from a dict
app_core_responses_base_base_response_analysis_tags2_from_dict = AppCoreResponsesBaseBaseResponseAnalysisTags2.from_dict(app_core_responses_base_base_response_analysis_tags2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


