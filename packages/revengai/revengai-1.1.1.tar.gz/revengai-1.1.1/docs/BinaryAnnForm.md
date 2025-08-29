# BinaryAnnForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **float** | Confidence of the annotation | [optional] [default to 0.0]
**nns** | **int** | Number of nearest neighbors | [optional] [default to 1]
**collection_ids** | **List[int]** | Collection IDs to search for nearest neighbors | [optional] 
**binary_ids** | **List[int]** | Binary IDs to search for nearest neighbors | [optional] 

## Example

```python
from revengai.models.binary_ann_form import BinaryAnnForm

# TODO update the JSON string below
json = "{}"
# create an instance of BinaryAnnForm from a JSON string
binary_ann_form_instance = BinaryAnnForm.from_json(json)
# print the JSON string representation of the object
print(BinaryAnnForm.to_json())

# convert the object into a dict
binary_ann_form_dict = binary_ann_form_instance.to_dict()
# create an instance of BinaryAnnForm from a dict
binary_ann_form_from_dict = BinaryAnnForm.from_dict(binary_ann_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


