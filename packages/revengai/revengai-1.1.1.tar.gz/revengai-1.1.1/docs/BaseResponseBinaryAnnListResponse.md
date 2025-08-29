# BaseResponseBinaryAnnListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **bool** | Response status on whether the request succeeded | [optional] [default to True]
**data** | [**BinaryAnnListResponse**](BinaryAnnListResponse.md) |  | [optional] 
**message** | **str** |  | [optional] 
**errors** | [**List[ErrorModel]**](ErrorModel.md) |  | [optional] 
**meta** | [**MetaModel**](MetaModel.md) | Metadata | [optional] 

## Example

```python
from revengai.models.base_response_binary_ann_list_response import BaseResponseBinaryAnnListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BaseResponseBinaryAnnListResponse from a JSON string
base_response_binary_ann_list_response_instance = BaseResponseBinaryAnnListResponse.from_json(json)
# print the JSON string representation of the object
print(BaseResponseBinaryAnnListResponse.to_json())

# convert the object into a dict
base_response_binary_ann_list_response_dict = base_response_binary_ann_list_response_instance.to_dict()
# create an instance of BaseResponseBinaryAnnListResponse from a dict
base_response_binary_ann_list_response_from_dict = BaseResponseBinaryAnnListResponse.from_dict(base_response_binary_ann_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


