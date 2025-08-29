# mlx.api.model_registry.PublicApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_file**](PublicApi.md#get_file) | **GET** /public/projects/{project_name}/models/{model_name}/versions/{version_name}/files/{file_name} | Download file from public path
[**get_models**](PublicApi.md#get_models) | **GET** /public/models | List public models


# **get_file**
> bytearray get_file(project_name, model_name, version_name, file_name, range)

Download file from public path

Download file from public path

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v1
# See configuration.py for a list of all supported configuration parameters.
configuration = mlx.api.model_registry.Configuration(
    host = "/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = mlx.api.model_registry.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with mlx.api.model_registry.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = mlx.api.model_registry.PublicApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name
    file_name = 'file_name_example' # str | File name
    range = 'range_example' # str | File bytes range

    try:
        # Download file from public path
        api_response = api_instance.get_file(project_name, model_name, version_name, file_name, range)
        print("The response of PublicApi->get_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_name** | **str**| Version name | 
 **file_name** | **str**| File name | 
 **range** | **str**| File bytes range | 

### Return type

**bytearray**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success response |  * Content-Length - Response content bytes length <br>  * Content-Range - Bytes range of downloaded content <br>  * Content-Type - Content type of downloaded file <br>  |
**400** | Bad request |  -  |
**403** | Forbidden Model |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_models**
> ModelsResponse get_models(ascending=ascending, page=page, page_size=page_size, search=search, sort_by=sort_by, tags=tags)

List public models

List public models

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.models_response import ModelsResponse
from mlx.api.model_registry.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v1
# See configuration.py for a list of all supported configuration parameters.
configuration = mlx.api.model_registry.Configuration(
    host = "/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = mlx.api.model_registry.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with mlx.api.model_registry.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = mlx.api.model_registry.PublicApi(api_client)
    ascending = True # bool |  (optional)
    page = 56 # int |  (optional)
    page_size = 56 # int |  (optional)
    search = 'search_example' # str |  (optional)
    sort_by = 'sort_by_example' # str |  (optional)
    tags = ['tags_example'] # List[str] |  (optional)

    try:
        # List public models
        api_response = api_instance.get_models(ascending=ascending, page=page, page_size=page_size, search=search, sort_by=sort_by, tags=tags)
        print("The response of PublicApi->get_models:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_models: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ascending** | **bool**|  | [optional] 
 **page** | **int**|  | [optional] 
 **page_size** | **int**|  | [optional] 
 **search** | **str**|  | [optional] 
 **sort_by** | **str**|  | [optional] 
 **tags** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**ModelsResponse**](ModelsResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

