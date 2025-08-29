# ModelRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**labels** | **Dict[str, str]** |  | [optional] 
**name** | **str** |  | 
**public** | **bool** |  | [optional] 
**storage** | **str** |  | [optional] 
**summary** | **str** |  | [optional] 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from mlx.api.model_registry.models.model_request import ModelRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ModelRequest from a JSON string
model_request_instance = ModelRequest.from_json(json)
# print the JSON string representation of the object
print(ModelRequest.to_json())

# convert the object into a dict
model_request_dict = model_request_instance.to_dict()
# create an instance of ModelRequest from a dict
model_request_from_dict = ModelRequest.from_dict(model_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


