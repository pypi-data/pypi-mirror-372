# ANNFunction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**limit** | **int** | The amount of neighbours per function ID | [optional] [default to 5]
**distance** | **float** | The distance between two neighbours | [optional] [default to 0.1]
**analysis_search_ids** | **List[Optional[int]]** | Perform a search on functions within a list of analyses | [optional] [default to []]
**collection_search_ids** | **List[Optional[int]]** | Search only within these collections | [optional] [default to []]
**search_binary_ids** | [**SearchBinaryIds**](SearchBinaryIds.md) |  | [optional] 
**search_function_ids** | [**SearchFunctionIds**](SearchFunctionIds.md) |  | [optional] 
**debug_only** | **bool** | Searches for only functions which are debug | [optional] [default to False]

## Example

```python
from revengai.models.ann_function import ANNFunction

# TODO update the JSON string below
json = "{}"
# create an instance of ANNFunction from a JSON string
ann_function_instance = ANNFunction.from_json(json)
# print the JSON string representation of the object
print(ANNFunction.to_json())

# convert the object into a dict
ann_function_dict = ann_function_instance.to_dict()
# create an instance of ANNFunction from a dict
ann_function_from_dict = ANNFunction.from_dict(ann_function_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


