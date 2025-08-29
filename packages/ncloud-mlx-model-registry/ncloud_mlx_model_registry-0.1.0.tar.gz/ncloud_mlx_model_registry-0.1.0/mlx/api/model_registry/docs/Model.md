# Model


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created** | **str** |  | 
**description** | **str** |  | 
**id** | **str** |  | 
**labels** | **Dict[str, str]** |  | 
**name** | **str** |  | 
**project** | **str** |  | 
**project_id** | **str** |  | 
**public** | **bool** |  | 
**storage** | [**ModelStorage**](ModelStorage.md) |  | 
**summary** | **str** |  | 
**tags** | **List[str]** |  | 
**updated** | **str** |  | 

## Example

```python
from mlx.api.model_registry.models.model import Model

# TODO update the JSON string below
json = "{}"
# create an instance of Model from a JSON string
model_instance = Model.from_json(json)
# print the JSON string representation of the object
print(Model.to_json())

# convert the object into a dict
model_dict = model_instance.to_dict()
# create an instance of Model from a dict
model_from_dict = Model.from_dict(model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


