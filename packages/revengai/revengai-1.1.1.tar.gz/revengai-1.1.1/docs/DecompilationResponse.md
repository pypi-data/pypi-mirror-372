# DecompilationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**function_id** | **int** |  | 
**decompilation** | **str** |  | 
**calling_convention** | **str** |  | 

## Example

```python
from revengai.models.decompilation_response import DecompilationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DecompilationResponse from a JSON string
decompilation_response_instance = DecompilationResponse.from_json(json)
# print the JSON string representation of the object
print(DecompilationResponse.to_json())

# convert the object into a dict
decompilation_response_dict = decompilation_response_instance.to_dict()
# create an instance of DecompilationResponse from a dict
decompilation_response_from_dict = DecompilationResponse.from_dict(decompilation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


