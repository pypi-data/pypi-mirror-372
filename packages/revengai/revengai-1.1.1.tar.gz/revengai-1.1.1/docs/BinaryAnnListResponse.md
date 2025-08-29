# BinaryAnnListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**list** | [**List[ExportedBinaryAnnResult]**](ExportedBinaryAnnResult.md) |  | 

## Example

```python
from revengai.models.binary_ann_list_response import BinaryAnnListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BinaryAnnListResponse from a JSON string
binary_ann_list_response_instance = BinaryAnnListResponse.from_json(json)
# print the JSON string representation of the object
print(BinaryAnnListResponse.to_json())

# convert the object into a dict
binary_ann_list_response_dict = binary_ann_list_response_instance.to_dict()
# create an instance of BinaryAnnListResponse from a dict
binary_ann_list_response_from_dict = BinaryAnnListResponse.from_dict(binary_ann_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


