# SymbolsInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base_addr** | **int** |  | [optional] 
**provided_boundaries** | [**Boundary**](Boundary.md) |  | [optional] 

## Example

```python
from revengai.models.symbols_info import SymbolsInfo

# TODO update the JSON string below
json = "{}"
# create an instance of SymbolsInfo from a JSON string
symbols_info_instance = SymbolsInfo.from_json(json)
# print the JSON string representation of the object
print(SymbolsInfo.to_json())

# convert the object into a dict
symbols_info_dict = symbols_info_instance.to_dict()
# create an instance of SymbolsInfo from a dict
symbols_info_from_dict = SymbolsInfo.from_dict(symbols_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


