# mlx.api.model_registry.VersionsApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_version**](VersionsApi.md#create_version) | **POST** /projects/{project_name}/models/{model_name}/versions | Create a new model version entry
[**delete_version**](VersionsApi.md#delete_version) | **DELETE** /projects/{project_name}/models/{model_name}/versions/{version_name} | Delete model version (including files)
[**finalize_upload**](VersionsApi.md#finalize_upload) | **POST** /private/projects/{project_name}/models/{model_name}/versions/{version_name}/finalize-upload | Finalize model version upload
[**get_latest_model_version**](VersionsApi.md#get_latest_model_version) | **GET** /projects/{project_name}/models/{model_name}/latest | Get latest model version
[**get_version**](VersionsApi.md#get_version) | **GET** /projects/{project_name}/models/{model_name}/versions/{version_name} | Get model version information
[**get_versions**](VersionsApi.md#get_versions) | **GET** /projects/{project_name}/models/{model_name}/versions | List verisons for some ids
[**list_versions_by_ids**](VersionsApi.md#list_versions_by_ids) | **POST** /projects/{project_name}/models/{model_name}/list | List verisons for some ids
[**update_version**](VersionsApi.md#update_version) | **PATCH** /projects/{project_name}/models/{model_name}/versions/{version_name} | Update model version metadata


# **create_version**
> Version create_version(project_name, model_name, version_request)

Create a new model version entry

Create a new model version entry

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.version import Version
from mlx.api.model_registry.models.version_request import VersionRequest
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
    api_instance = mlx.api.model_registry.VersionsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_request = mlx.api.model_registry.VersionRequest() # VersionRequest | 

    try:
        # Create a new model version entry
        api_response = api_instance.create_version(project_name, model_name, version_request)
        print("The response of VersionsApi->create_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->create_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_request** | [**VersionRequest**](VersionRequest.md)|  | 

### Return type

[**Version**](Version.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Ok |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_version**
> delete_version(project_name, model_name, version_name)

Delete model version (including files)

Delete model version (including files)

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
    api_instance = mlx.api.model_registry.VersionsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name

    try:
        # Delete model version (including files)
        api_instance.delete_version(project_name, model_name, version_name)
    except Exception as e:
        print("Exception when calling VersionsApi->delete_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_name** | **str**| Version name | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | No content |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **finalize_upload**
> Version finalize_upload(project_name, model_name, version_name)

Finalize model version upload

Finalize model version upload

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
    api_instance = mlx.api.model_registry.VersionsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name

    try:
        # Finalize model version upload
        api_response = api_instance.finalize_upload(project_name, model_name, version_name)
        print("The response of VersionsApi->finalize_upload:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->finalize_upload: %s\n" % e)
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
**200** | OK |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_latest_model_version**
> Version get_latest_model_version(project_name, model_name)

Get latest model version

Get latest model version

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
    api_instance = mlx.api.model_registry.VersionsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name

    try:
        # Get latest model version
        api_response = api_instance.get_latest_model_version(project_name, model_name)
        print("The response of VersionsApi->get_latest_model_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->get_latest_model_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 

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

# **get_version**
> Version get_version(project_name, model_name, version_name)

Get model version information

Get model version information

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
    api_instance = mlx.api.model_registry.VersionsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name

    try:
        # Get model version information
        api_response = api_instance.get_version(project_name, model_name, version_name)
        print("The response of VersionsApi->get_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->get_version: %s\n" % e)
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

# **get_versions**
> VersionsResponse get_versions(project_name, model_name, ascending=ascending, page=page, page_size=page_size, search=search, sort_by=sort_by, tags=tags)

List verisons for some ids

List verisons for some ids

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.versions_response import VersionsResponse
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
    api_instance = mlx.api.model_registry.VersionsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    ascending = True # bool |  (optional)
    page = 56 # int |  (optional)
    page_size = 56 # int |  (optional)
    search = 'search_example' # str |  (optional)
    sort_by = 'sort_by_example' # str |  (optional)
    tags = ['tags_example'] # List[str] |  (optional)

    try:
        # List verisons for some ids
        api_response = api_instance.get_versions(project_name, model_name, ascending=ascending, page=page, page_size=page_size, search=search, sort_by=sort_by, tags=tags)
        print("The response of VersionsApi->get_versions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->get_versions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **ascending** | **bool**|  | [optional] 
 **page** | **int**|  | [optional] 
 **page_size** | **int**|  | [optional] 
 **search** | **str**|  | [optional] 
 **sort_by** | **str**|  | [optional] 
 **tags** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**VersionsResponse**](VersionsResponse.md)

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

# **list_versions_by_ids**
> VersionListRequest list_versions_by_ids(project_name, model_name, version_list_request, ascending=ascending, page=page, page_size=page_size, search=search, sort_by=sort_by, tags=tags)

List verisons for some ids

List verisons for some ids

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.version_list_request import VersionListRequest
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
    api_instance = mlx.api.model_registry.VersionsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_list_request = mlx.api.model_registry.VersionListRequest() # VersionListRequest | 
    ascending = True # bool |  (optional)
    page = 56 # int |  (optional)
    page_size = 56 # int |  (optional)
    search = 'search_example' # str |  (optional)
    sort_by = 'sort_by_example' # str |  (optional)
    tags = ['tags_example'] # List[str] |  (optional)

    try:
        # List verisons for some ids
        api_response = api_instance.list_versions_by_ids(project_name, model_name, version_list_request, ascending=ascending, page=page, page_size=page_size, search=search, sort_by=sort_by, tags=tags)
        print("The response of VersionsApi->list_versions_by_ids:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->list_versions_by_ids: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_list_request** | [**VersionListRequest**](VersionListRequest.md)|  | 
 **ascending** | **bool**|  | [optional] 
 **page** | **int**|  | [optional] 
 **page_size** | **int**|  | [optional] 
 **search** | **str**|  | [optional] 
 **sort_by** | **str**|  | [optional] 
 **tags** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**VersionListRequest**](VersionListRequest.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Ok |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_version**
> Version update_version(project_name, model_name, version_name, version_update_request)

Update model version metadata

Update model version metadata

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.version import Version
from mlx.api.model_registry.models.version_update_request import VersionUpdateRequest
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
    api_instance = mlx.api.model_registry.VersionsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name
    version_update_request = mlx.api.model_registry.VersionUpdateRequest() # VersionUpdateRequest | 

    try:
        # Update model version metadata
        api_response = api_instance.update_version(project_name, model_name, version_name, version_update_request)
        print("The response of VersionsApi->update_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VersionsApi->update_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_name** | **str**| Version name | 
 **version_update_request** | [**VersionUpdateRequest**](VersionUpdateRequest.md)|  | 

### Return type

[**Version**](Version.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

