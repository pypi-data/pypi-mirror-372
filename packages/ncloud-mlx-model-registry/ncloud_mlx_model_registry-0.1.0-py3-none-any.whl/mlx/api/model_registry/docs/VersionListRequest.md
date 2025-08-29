# VersionListRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | **List[str]** |  | 

## Example

```python
from mlx.api.model_registry.models.version_list_request import VersionListRequest

# TODO update the JSON string below
json = "{}"
# create an instance of VersionListRequest from a JSON string
version_list_request_instance = VersionListRequest.from_json(json)
# print the JSON string representation of the object
print(VersionListRequest.to_json())

# convert the object into a dict
version_list_request_dict = version_list_request_instance.to_dict()
# create an instance of VersionListRequest from a dict
version_list_request_from_dict = VersionListRequest.from_dict(version_list_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


