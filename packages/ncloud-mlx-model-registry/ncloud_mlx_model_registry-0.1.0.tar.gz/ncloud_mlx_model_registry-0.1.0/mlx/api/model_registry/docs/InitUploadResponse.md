# InitUploadResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**part_size** | **int** |  | [optional] 
**skip_body** | **bool** |  | [optional] 
**upload_key** | **str** |  | [optional] 

## Example

```python
from mlx.api.model_registry.models.init_upload_response import InitUploadResponse

# TODO update the JSON string below
json = "{}"
# create an instance of InitUploadResponse from a JSON string
init_upload_response_instance = InitUploadResponse.from_json(json)
# print the JSON string representation of the object
print(InitUploadResponse.to_json())

# convert the object into a dict
init_upload_response_dict = init_upload_response_instance.to_dict()
# create an instance of InitUploadResponse from a dict
init_upload_response_from_dict = InitUploadResponse.from_dict(init_upload_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


