# NearestNeighbor


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**distance** | **float** |  | 
**nearest_neighbor_analysis_id** | **int** |  | 
**nearest_neighbor_analysis_name** | **str** |  | 
**nearest_neighbor_function_name** | **str** |  | 
**nearest_neighbor_function_name_mangled** | **str** |  | 
**nearest_neighbor_binary_id** | **int** |  | 
**nearest_neighbor_sha_256_hash** | **str** |  | 
**nearest_neighbor_debug** | **bool** |  | 

## Example

```python
from revengai.models.nearest_neighbor import NearestNeighbor

# TODO update the JSON string below
json = "{}"
# create an instance of NearestNeighbor from a JSON string
nearest_neighbor_instance = NearestNeighbor.from_json(json)
# print the JSON string representation of the object
print(NearestNeighbor.to_json())

# convert the object into a dict
nearest_neighbor_dict = nearest_neighbor_instance.to_dict()
# create an instance of NearestNeighbor from a dict
nearest_neighbor_from_dict = NearestNeighbor.from_dict(nearest_neighbor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


