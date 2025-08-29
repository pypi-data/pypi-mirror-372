# ModelStorage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_class** | **str** |  | 

## Example

```python
from mlx.api.model_registry.models.model_storage import ModelStorage

# TODO update the JSON string below
json = "{}"
# create an instance of ModelStorage from a JSON string
model_storage_instance = ModelStorage.from_json(json)
# print the JSON string representation of the object
print(ModelStorage.to_json())

# convert the object into a dict
model_storage_dict = model_storage_instance.to_dict()
# create an instance of ModelStorage from a dict
model_storage_from_dict = ModelStorage.from_dict(model_storage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


