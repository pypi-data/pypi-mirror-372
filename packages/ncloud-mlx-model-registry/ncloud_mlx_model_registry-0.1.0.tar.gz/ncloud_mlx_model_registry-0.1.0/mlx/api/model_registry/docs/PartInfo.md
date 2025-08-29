# PartInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**number** | **int** |  | 

## Example

```python
from mlx.api.model_registry.models.part_info import PartInfo

# TODO update the JSON string below
json = "{}"
# create an instance of PartInfo from a JSON string
part_info_instance = PartInfo.from_json(json)
# print the JSON string representation of the object
print(PartInfo.to_json())

# convert the object into a dict
part_info_dict = part_info_instance.to_dict()
# create an instance of PartInfo from a dict
part_info_from_dict = PartInfo.from_dict(part_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


