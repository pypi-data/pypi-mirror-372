# VersionRequest


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
**version** | **str** |  | 

## Example

```python
from mlx.api.model_registry.models.version_request import VersionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of VersionRequest from a JSON string
version_request_instance = VersionRequest.from_json(json)
# print the JSON string representation of the object
print(VersionRequest.to_json())

# convert the object into a dict
version_request_dict = version_request_instance.to_dict()
# create an instance of VersionRequest from a dict
version_request_from_dict = VersionRequest.from_dict(version_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


