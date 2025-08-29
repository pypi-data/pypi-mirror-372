# BaseResponseBoxPlotConfidence


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **bool** | Response status on whether the request succeeded | [optional] [default to True]
**data** | [**BoxPlotConfidence**](BoxPlotConfidence.md) |  | [optional] 
**message** | **str** |  | [optional] 
**errors** | [**List[ErrorModel]**](ErrorModel.md) |  | [optional] 
**meta** | [**MetaModel**](MetaModel.md) | Metadata | [optional] 

## Example

```python
from revengai.models.base_response_box_plot_confidence import BaseResponseBoxPlotConfidence

# TODO update the JSON string below
json = "{}"
# create an instance of BaseResponseBoxPlotConfidence from a JSON string
base_response_box_plot_confidence_instance = BaseResponseBoxPlotConfidence.from_json(json)
# print the JSON string representation of the object
print(BaseResponseBoxPlotConfidence.to_json())

# convert the object into a dict
base_response_box_plot_confidence_dict = base_response_box_plot_confidence_instance.to_dict()
# create an instance of BaseResponseBoxPlotConfidence from a dict
base_response_box_plot_confidence_from_dict = BaseResponseBoxPlotConfidence.from_dict(base_response_box_plot_confidence_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


