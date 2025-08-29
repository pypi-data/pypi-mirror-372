# TagOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tag** | **str** | The name of the tag | 
**origin** | **str** | Where the tag originates from | 

## Example

```python
from revengai.models.tag_output import TagOutput

# TODO update the JSON string below
json = "{}"
# create an instance of TagOutput from a JSON string
tag_output_instance = TagOutput.from_json(json)
# print the JSON string representation of the object
print(TagOutput.to_json())

# convert the object into a dict
tag_output_dict = tag_output_instance.to_dict()
# create an instance of TagOutput from a dict
tag_output_from_dict = TagOutput.from_dict(tag_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


