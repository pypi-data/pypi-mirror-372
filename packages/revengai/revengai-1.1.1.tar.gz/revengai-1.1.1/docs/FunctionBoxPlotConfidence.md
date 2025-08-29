# FunctionBoxPlotConfidence


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**function_id** | **int** |  | 
**box_plot** | [**BoxPlotConfidence**](BoxPlotConfidence.md) |  | 

## Example

```python
from revengai.models.function_box_plot_confidence import FunctionBoxPlotConfidence

# TODO update the JSON string below
json = "{}"
# create an instance of FunctionBoxPlotConfidence from a JSON string
function_box_plot_confidence_instance = FunctionBoxPlotConfidence.from_json(json)
# print the JSON string representation of the object
print(FunctionBoxPlotConfidence.to_json())

# convert the object into a dict
function_box_plot_confidence_dict = function_box_plot_confidence_instance.to_dict()
# create an instance of FunctionBoxPlotConfidence from a dict
function_box_plot_confidence_from_dict = FunctionBoxPlotConfidence.from_dict(function_box_plot_confidence_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


