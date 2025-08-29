# FunctionNameInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**function_id** | **int** |  | 
**function_name** | **str** |  | 

## Example

```python
from revengai.models.function_name_input import FunctionNameInput

# TODO update the JSON string below
json = "{}"
# create an instance of FunctionNameInput from a JSON string
function_name_input_instance = FunctionNameInput.from_json(json)
# print the JSON string representation of the object
print(FunctionNameInput.to_json())

# convert the object into a dict
function_name_input_dict = function_name_input_instance.to_dict()
# create an instance of FunctionNameInput from a dict
function_name_input_from_dict = FunctionNameInput.from_dict(function_name_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


