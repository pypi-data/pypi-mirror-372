# BaseResponseSymbolsInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **bool** | Response status on whether the request succeeded | [optional] [default to True]
**data** | [**SymbolsInfo**](SymbolsInfo.md) |  | [optional] 
**message** | **str** |  | [optional] 
**errors** | [**List[ErrorModel]**](ErrorModel.md) |  | [optional] 
**meta** | [**MetaModel**](MetaModel.md) | Metadata | [optional] 

## Example

```python
from revengai.models.base_response_symbols_info import BaseResponseSymbolsInfo

# TODO update the JSON string below
json = "{}"
# create an instance of BaseResponseSymbolsInfo from a JSON string
base_response_symbols_info_instance = BaseResponseSymbolsInfo.from_json(json)
# print the JSON string representation of the object
print(BaseResponseSymbolsInfo.to_json())

# convert the object into a dict
base_response_symbols_info_dict = base_response_symbols_info_instance.to_dict()
# create an instance of BaseResponseSymbolsInfo from a dict
base_response_symbols_info_from_dict = BaseResponseSymbolsInfo.from_dict(base_response_symbols_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


