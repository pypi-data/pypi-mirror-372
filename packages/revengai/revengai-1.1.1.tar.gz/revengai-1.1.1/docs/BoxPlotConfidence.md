# BoxPlotConfidence

Format for confidence - returned in the box plot format

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**min** | **float** |  | 
**max** | **float** |  | 
**average** | **float** |  | 
**upper_quartile** | **float** |  | 
**lower_quartile** | **float** |  | 
**positive_count** | **int** |  | 
**negative_count** | **int** |  | 

## Example

```python
from revengai.models.box_plot_confidence import BoxPlotConfidence

# TODO update the JSON string below
json = "{}"
# create an instance of BoxPlotConfidence from a JSON string
box_plot_confidence_instance = BoxPlotConfidence.from_json(json)
# print the JSON string representation of the object
print(BoxPlotConfidence.to_json())

# convert the object into a dict
box_plot_confidence_dict = box_plot_confidence_instance.to_dict()
# create an instance of BoxPlotConfidence from a dict
box_plot_confidence_from_dict = BoxPlotConfidence.from_dict(box_plot_confidence_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


