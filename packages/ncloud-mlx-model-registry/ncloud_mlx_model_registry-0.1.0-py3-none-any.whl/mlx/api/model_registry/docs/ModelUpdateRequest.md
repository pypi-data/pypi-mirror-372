# ModelUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**labels** | **Dict[str, str]** |  | [optional] 
**public** | **bool** |  | [optional] 
**summary** | **str** |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from mlx.api.model_registry.models.model_update_request import ModelUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ModelUpdateRequest from a JSON string
model_update_request_instance = ModelUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(ModelUpdateRequest.to_json())

# convert the object into a dict
model_update_request_dict = model_update_request_instance.to_dict()
# create an instance of ModelUpdateRequest from a dict
model_update_request_from_dict = ModelUpdateRequest.from_dict(model_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


