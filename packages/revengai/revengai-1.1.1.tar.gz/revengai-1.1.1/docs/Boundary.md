# Boundary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start_addr** | **int** | Start address of the function boundary | 
**end_addr** | **int** | End address of the function boundary | 
**name** | **str** | Name of the function | 

## Example

```python
from revengai.models.boundary import Boundary

# TODO update the JSON string below
json = "{}"
# create an instance of Boundary from a JSON string
boundary_instance = Boundary.from_json(json)
# print the JSON string representation of the object
print(Boundary.to_json())

# convert the object into a dict
boundary_dict = boundary_instance.to_dict()
# create an instance of Boundary from a dict
boundary_from_dict = Boundary.from_dict(boundary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


