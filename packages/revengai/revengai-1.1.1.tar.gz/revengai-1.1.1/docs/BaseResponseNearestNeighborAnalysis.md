# BaseResponseNearestNeighborAnalysis


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **bool** | Response status on whether the request succeeded | [optional] [default to True]
**data** | **Dict[str, Dict[str, NearestNeighbor]]** |  | [optional] 
**message** | **str** |  | [optional] 
**errors** | [**List[ErrorModel]**](ErrorModel.md) |  | [optional] 
**meta** | [**MetaModel**](MetaModel.md) | Metadata | [optional] 

## Example

```python
from revengai.models.base_response_nearest_neighbor_analysis import BaseResponseNearestNeighborAnalysis

# TODO update the JSON string below
json = "{}"
# create an instance of BaseResponseNearestNeighborAnalysis from a JSON string
base_response_nearest_neighbor_analysis_instance = BaseResponseNearestNeighborAnalysis.from_json(json)
# print the JSON string representation of the object
print(BaseResponseNearestNeighborAnalysis.to_json())

# convert the object into a dict
base_response_nearest_neighbor_analysis_dict = base_response_nearest_neighbor_analysis_instance.to_dict()
# create an instance of BaseResponseNearestNeighborAnalysis from a dict
base_response_nearest_neighbor_analysis_from_dict = BaseResponseNearestNeighborAnalysis.from_dict(base_response_nearest_neighbor_analysis_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


