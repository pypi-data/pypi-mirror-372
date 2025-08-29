# BaseResponseListFunctionBoxPlotConfidence


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **bool** | Response status on whether the request succeeded | [optional] [default to True]
**data** | [**List[FunctionBoxPlotConfidence]**](FunctionBoxPlotConfidence.md) |  | [optional] 
**message** | **str** |  | [optional] 
**errors** | [**List[ErrorModel]**](ErrorModel.md) |  | [optional] 
**meta** | [**MetaModel**](MetaModel.md) | Metadata | [optional] 

## Example

```python
from revengai.models.base_response_list_function_box_plot_confidence import BaseResponseListFunctionBoxPlotConfidence

# TODO update the JSON string below
json = "{}"
# create an instance of BaseResponseListFunctionBoxPlotConfidence from a JSON string
base_response_list_function_box_plot_confidence_instance = BaseResponseListFunctionBoxPlotConfidence.from_json(json)
# print the JSON string representation of the object
print(BaseResponseListFunctionBoxPlotConfidence.to_json())

# convert the object into a dict
base_response_list_function_box_plot_confidence_dict = base_response_list_function_box_plot_confidence_instance.to_dict()
# create an instance of BaseResponseListFunctionBoxPlotConfidence from a dict
base_response_list_function_box_plot_confidence_from_dict = BaseResponseListFunctionBoxPlotConfidence.from_dict(base_response_list_function_box_plot_confidence_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


