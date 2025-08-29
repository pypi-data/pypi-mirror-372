# FunctionNameConfidenceBody


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**functions** | [**List[FunctionNameInput]**](FunctionNameInput.md) | List of function ids and the function names they want to check confidence for | [optional] 
**is_debug** | **bool** | Flag to match only to a debug function | [optional] [default to False]

## Example

```python
from revengai.models.function_name_confidence_body import FunctionNameConfidenceBody

# TODO update the JSON string below
json = "{}"
# create an instance of FunctionNameConfidenceBody from a JSON string
function_name_confidence_body_instance = FunctionNameConfidenceBody.from_json(json)
# print the JSON string representation of the object
print(FunctionNameConfidenceBody.to_json())

# convert the object into a dict
function_name_confidence_body_dict = function_name_confidence_body_instance.to_dict()
# create an instance of FunctionNameConfidenceBody from a dict
function_name_confidence_body_from_dict = FunctionNameConfidenceBody.from_dict(function_name_confidence_body_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


