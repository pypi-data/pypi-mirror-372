# TagConfidenceBody


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tags** | [**List[Tags]**](Tags.md) |  | 

## Example

```python
from revengai.models.tag_confidence_body import TagConfidenceBody

# TODO update the JSON string below
json = "{}"
# create an instance of TagConfidenceBody from a JSON string
tag_confidence_body_instance = TagConfidenceBody.from_json(json)
# print the JSON string representation of the object
print(TagConfidenceBody.to_json())

# convert the object into a dict
tag_confidence_body_dict = tag_confidence_body_instance.to_dict()
# create an instance of TagConfidenceBody from a dict
tag_confidence_body_from_dict = TagConfidenceBody.from_dict(tag_confidence_body_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


