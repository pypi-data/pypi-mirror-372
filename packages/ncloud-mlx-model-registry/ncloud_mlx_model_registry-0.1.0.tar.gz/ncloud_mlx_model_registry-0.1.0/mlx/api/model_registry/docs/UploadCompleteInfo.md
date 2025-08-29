# UploadCompleteInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parts** | [**List[PartInfo]**](PartInfo.md) |  | 

## Example

```python
from mlx.api.model_registry.models.upload_complete_info import UploadCompleteInfo

# TODO update the JSON string below
json = "{}"
# create an instance of UploadCompleteInfo from a JSON string
upload_complete_info_instance = UploadCompleteInfo.from_json(json)
# print the JSON string representation of the object
print(UploadCompleteInfo.to_json())

# convert the object into a dict
upload_complete_info_dict = upload_complete_info_instance.to_dict()
# create an instance of UploadCompleteInfo from a dict
upload_complete_info_from_dict = UploadCompleteInfo.from_dict(upload_complete_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


