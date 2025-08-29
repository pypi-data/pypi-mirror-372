# AppApiRestV2InfoResponsesAnalysisTags


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**analysis_tags** | [**List[TagOutput]**](TagOutput.md) | List of analysis tags | 
**suggested_tags** | [**List[TagOutput]**](TagOutput.md) | List of suggested analysis tags | 

## Example

```python
from revengai.models.app_api_rest_v2_info_responses_analysis_tags import AppApiRestV2InfoResponsesAnalysisTags

# TODO update the JSON string below
json = "{}"
# create an instance of AppApiRestV2InfoResponsesAnalysisTags from a JSON string
app_api_rest_v2_info_responses_analysis_tags_instance = AppApiRestV2InfoResponsesAnalysisTags.from_json(json)
# print the JSON string representation of the object
print(AppApiRestV2InfoResponsesAnalysisTags.to_json())

# convert the object into a dict
app_api_rest_v2_info_responses_analysis_tags_dict = app_api_rest_v2_info_responses_analysis_tags_instance.to_dict()
# create an instance of AppApiRestV2InfoResponsesAnalysisTags from a dict
app_api_rest_v2_info_responses_analysis_tags_from_dict = AppApiRestV2InfoResponsesAnalysisTags.from_dict(app_api_rest_v2_info_responses_analysis_tags_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


