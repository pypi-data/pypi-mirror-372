# VersionUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author** | **str** |  | [optional] 
**labels** | **Dict[str, str]** |  | [optional] 
**stage** | **str** |  | [optional] 
**storage** | [**VersionStorage**](VersionStorage.md) |  | [optional] 
**summary** | **str** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**training** | [**Training**](Training.md) |  | [optional] 

## Example

```python
from mlx.api.model_registry.models.version_update_request import VersionUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of VersionUpdateRequest from a JSON string
version_update_request_instance = VersionUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(VersionUpdateRequest.to_json())

# convert the object into a dict
version_update_request_dict = version_update_request_instance.to_dict()
# create an instance of VersionUpdateRequest from a dict
version_update_request_from_dict = VersionUpdateRequest.from_dict(version_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


