# SimilarFunctionsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**function_id** | **int** |  | 
**function_name** | **str** |  | 
**binary_id** | **int** |  | 
**binary_name** | **str** |  | 
**distance** | **float** |  | 
**embedding_3d** | **List[float]** |  | 
**embedding_1d** | **List[float]** |  | 
**sha_256_hash** | **str** |  | 

## Example

```python
from revengai.models.similar_functions_response import SimilarFunctionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SimilarFunctionsResponse from a JSON string
similar_functions_response_instance = SimilarFunctionsResponse.from_json(json)
# print the JSON string representation of the object
print(SimilarFunctionsResponse.to_json())

# convert the object into a dict
similar_functions_response_dict = similar_functions_response_instance.to_dict()
# create an instance of SimilarFunctionsResponse from a dict
similar_functions_response_from_dict = SimilarFunctionsResponse.from_dict(similar_functions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


