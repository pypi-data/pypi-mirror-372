# AppApiRestV2AnalysesResponsesAnalysisTags


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**analysis_tags** | [**List[AppApiRestV2AnalysesResponsesTagItem]**](AppApiRestV2AnalysesResponsesTagItem.md) |  | 
**suggested_tags** | [**List[AppApiRestV2AnalysesResponsesTagItem]**](AppApiRestV2AnalysesResponsesTagItem.md) |  | 

## Example

```python
from revengai.models.app_api_rest_v2_analyses_responses_analysis_tags import AppApiRestV2AnalysesResponsesAnalysisTags

# TODO update the JSON string below
json = "{}"
# create an instance of AppApiRestV2AnalysesResponsesAnalysisTags from a JSON string
app_api_rest_v2_analyses_responses_analysis_tags_instance = AppApiRestV2AnalysesResponsesAnalysisTags.from_json(json)
# print the JSON string representation of the object
print(AppApiRestV2AnalysesResponsesAnalysisTags.to_json())

# convert the object into a dict
app_api_rest_v2_analyses_responses_analysis_tags_dict = app_api_rest_v2_analyses_responses_analysis_tags_instance.to_dict()
# create an instance of AppApiRestV2AnalysesResponsesAnalysisTags from a dict
app_api_rest_v2_analyses_responses_analysis_tags_from_dict = AppApiRestV2AnalysesResponsesAnalysisTags.from_dict(app_api_rest_v2_analyses_responses_analysis_tags_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


