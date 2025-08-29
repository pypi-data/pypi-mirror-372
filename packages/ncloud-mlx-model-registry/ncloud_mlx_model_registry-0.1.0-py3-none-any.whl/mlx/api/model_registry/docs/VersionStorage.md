# VersionStorage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**storage_type** | **str** |  | 

## Example

```python
from mlx.api.model_registry.models.version_storage import VersionStorage

# TODO update the JSON string below
json = "{}"
# create an instance of VersionStorage from a JSON string
version_storage_instance = VersionStorage.from_json(json)
# print the JSON string representation of the object
print(VersionStorage.to_json())

# convert the object into a dict
version_storage_dict = version_storage_instance.to_dict()
# create an instance of VersionStorage from a dict
version_storage_from_dict = VersionStorage.from_dict(version_storage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


