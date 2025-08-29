# Version


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**author** | **str** |  | 
**created** | **str** |  | 
**download_count** | **int** |  | 
**id** | **str** |  | 
**labels** | **Dict[str, str]** |  | 
**model** | **str** |  | 
**project** | **str** |  | 
**size** | **int** |  | 
**stage** | **str** |  | 
**storage** | [**VersionStorage**](VersionStorage.md) |  | 
**summary** | **str** |  | 
**tags** | **List[str]** |  | 
**training** | [**Training**](Training.md) |  | [optional] 
**updated** | **str** |  | 
**upload_done** | **bool** |  | 
**version_name** | **str** |  | 

## Example

```python
from mlx.api.model_registry.models.version import Version

# TODO update the JSON string below
json = "{}"
# create an instance of Version from a JSON string
version_instance = Version.from_json(json)
# print the JSON string representation of the object
print(Version.to_json())

# convert the object into a dict
version_dict = version_instance.to_dict()
# create an instance of Version from a dict
version_from_dict = Version.from_dict(version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


