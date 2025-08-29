# Training


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**environment** | [**Environment**](Environment.md) |  | 
**reference** | **str** |  | 
**source** | [**Source**](Source.md) |  | 

## Example

```python
from mlx.api.model_registry.models.training import Training

# TODO update the JSON string below
json = "{}"
# create an instance of Training from a JSON string
training_instance = Training.from_json(json)
# print the JSON string representation of the object
print(Training.to_json())

# convert the object into a dict
training_dict = training_instance.to_dict()
# create an instance of Training from a dict
training_from_dict = Training.from_dict(training_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


