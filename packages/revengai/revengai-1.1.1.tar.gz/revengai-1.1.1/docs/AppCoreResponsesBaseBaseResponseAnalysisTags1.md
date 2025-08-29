# AppCoreResponsesBaseBaseResponseAnalysisTags1


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **bool** | Response status on whether the request succeeded | [optional] [default to True]
**data** | [**AppApiRestV2InfoResponsesAnalysisTags**](AppApiRestV2InfoResponsesAnalysisTags.md) |  | [optional] 
**message** | **str** |  | [optional] 
**errors** | [**List[ErrorModel]**](ErrorModel.md) |  | [optional] 
**meta** | [**MetaModel**](MetaModel.md) | Metadata | [optional] 

## Example

```python
from revengai.models.app_core_responses_base_base_response_analysis_tags1 import AppCoreResponsesBaseBaseResponseAnalysisTags1

# TODO update the JSON string below
json = "{}"
# create an instance of AppCoreResponsesBaseBaseResponseAnalysisTags1 from a JSON string
app_core_responses_base_base_response_analysis_tags1_instance = AppCoreResponsesBaseBaseResponseAnalysisTags1.from_json(json)
# print the JSON string representation of the object
print(AppCoreResponsesBaseBaseResponseAnalysisTags1.to_json())

# convert the object into a dict
app_core_responses_base_base_response_analysis_tags1_dict = app_core_responses_base_base_response_analysis_tags1_instance.to_dict()
# create an instance of AppCoreResponsesBaseBaseResponseAnalysisTags1 from a dict
app_core_responses_base_base_response_analysis_tags1_from_dict = AppCoreResponsesBaseBaseResponseAnalysisTags1.from_dict(app_core_responses_base_base_response_analysis_tags1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


