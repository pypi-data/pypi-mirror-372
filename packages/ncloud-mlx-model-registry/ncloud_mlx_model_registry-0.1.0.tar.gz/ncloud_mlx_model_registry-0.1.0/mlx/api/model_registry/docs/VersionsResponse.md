# VersionsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model_versions** | [**List[Version]**](Version.md) |  | 
**total_count** | **int** |  | 

## Example

```python
from mlx.api.model_registry.models.versions_response import VersionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of VersionsResponse from a JSON string
versions_response_instance = VersionsResponse.from_json(json)
# print the JSON string representation of the object
print(VersionsResponse.to_json())

# convert the object into a dict
versions_response_dict = versions_response_instance.to_dict()
# create an instance of VersionsResponse from a dict
versions_response_from_dict = VersionsResponse.from_dict(versions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


