# ExportedBinaryAnnResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**analysis_id** | **int** |  | 
**binary_id** | **int** |  | 
**binary_name** | **str** |  | 
**sha_256_hash** | **str** |  | 
**analysis_scope** | **str** |  | 
**embedding_3d** | **List[float]** |  | 
**embedding_1d** | **List[float]** |  | 
**confidence** | **float** |  | 
**tags** | [**List[AppServicesBinaryAnnSchemaTagItem]**](AppServicesBinaryAnnSchemaTagItem.md) |  | [optional] 

## Example

```python
from revengai.models.exported_binary_ann_result import ExportedBinaryAnnResult

# TODO update the JSON string below
json = "{}"
# create an instance of ExportedBinaryAnnResult from a JSON string
exported_binary_ann_result_instance = ExportedBinaryAnnResult.from_json(json)
# print the JSON string representation of the object
print(ExportedBinaryAnnResult.to_json())

# convert the object into a dict
exported_binary_ann_result_dict = exported_binary_ann_result_instance.to_dict()
# create an instance of ExportedBinaryAnnResult from a dict
exported_binary_ann_result_from_dict = ExportedBinaryAnnResult.from_dict(exported_binary_ann_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


