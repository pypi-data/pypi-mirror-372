# FilesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contents** | [**List[File]**](File.md) |  | 
**continue_marker** | **str** |  | 

## Example

```python
from mlx.api.model_registry.models.files_response import FilesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FilesResponse from a JSON string
files_response_instance = FilesResponse.from_json(json)
# print the JSON string representation of the object
print(FilesResponse.to_json())

# convert the object into a dict
files_response_dict = files_response_instance.to_dict()
# create an instance of FilesResponse from a dict
files_response_from_dict = FilesResponse.from_dict(files_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


