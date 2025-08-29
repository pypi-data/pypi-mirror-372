# mlx.api.model_registry.PrivateApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**download_count**](PrivateApi.md#download_count) | **GET** /private/projects/{project_name}/models/{model_name}/versions/{version_name}/download-count | Create the download history entry for the model version


# **download_count**
> Version download_count(project_name, model_name, version_name)

Create the download history entry for the model version

Create the download history entry for the model version

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.version import Version
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
    api_instance = mlx.api.model_registry.PrivateApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name

    try:
        # Create the download history entry for the model version
        api_response = api_instance.download_count(project_name, model_name, version_name)
        print("The response of PrivateApi->download_count:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->download_count: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_name** | **str**| Version name | 

### Return type

[**Version**](Version.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Ok |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

