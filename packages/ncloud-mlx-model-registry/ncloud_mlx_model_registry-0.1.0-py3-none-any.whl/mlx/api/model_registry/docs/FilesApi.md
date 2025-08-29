# mlx.api.model_registry.FilesApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_file**](FilesApi.md#delete_file) | **DELETE** /projects/{project_name}/models/{model_name}/versions/{version_name}/files/{file_name} | Delete file
[**get_file**](FilesApi.md#get_file) | **GET** /projects/{project_name}/models/{model_name}/versions/{version_name}/files/{file_name} | Download file
[**get_files**](FilesApi.md#get_files) | **GET** /projects/{project_name}/models/{model_name}/versions/{version_name}/files | List files in requests diretory
[**init_or_complete_file**](FilesApi.md#init_or_complete_file) | **POST** /projects/{project_name}/models/{model_name}/versions/{version_name}/files/{file_name} | Start or complete parallel upload
[**put_file**](FilesApi.md#put_file) | **PUT** /projects/{project_name}/models/{model_name}/versions/{version_name}/files/{file_name} | Upload file contents


# **delete_file**
> delete_file(project_name, model_name, version_name)

Delete file

Delete file

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
    api_instance = mlx.api.model_registry.FilesApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name

    try:
        # Delete file
        api_instance.delete_file(project_name, model_name, version_name)
    except Exception as e:
        print("Exception when calling FilesApi->delete_file: %s\n" % e)
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

# **get_file**
> bytearray get_file(project_name, model_name, version_name, file_name, range)

Download file

Download file

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
    api_instance = mlx.api.model_registry.FilesApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name
    file_name = 'file_name_example' # str | File name
    range = 'range_example' # str | File bytes range

    try:
        # Download file
        api_response = api_instance.get_file(project_name, model_name, version_name, file_name, range)
        print("The response of FilesApi->get_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->get_file: %s\n" % e)
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
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_files**
> FilesResponse get_files(project_name, model_name, version_name, dir=dir, marker=marker, max_content=max_content)

List files in requests diretory

List files in requests diretory

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.files_response import FilesResponse
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
    api_instance = mlx.api.model_registry.FilesApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name
    dir = 'dir_example' # str |  (optional)
    marker = 'marker_example' # str |  (optional)
    max_content = 56 # int |  (optional)

    try:
        # List files in requests diretory
        api_response = api_instance.get_files(project_name, model_name, version_name, dir=dir, marker=marker, max_content=max_content)
        print("The response of FilesApi->get_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->get_files: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_name** | **str**| Version name | 
 **dir** | **str**|  | [optional] 
 **marker** | **str**|  | [optional] 
 **max_content** | **int**|  | [optional] 

### Return type

[**FilesResponse**](FilesResponse.md)

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

# **init_or_complete_file**
> InitUploadResponse init_or_complete_file(project_name, model_name, version_name)

Start or complete parallel upload

Start or complete parallel upload

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.init_upload_response import InitUploadResponse
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
    api_instance = mlx.api.model_registry.FilesApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name

    try:
        # Start or complete parallel upload
        api_response = api_instance.init_or_complete_file(project_name, model_name, version_name)
        print("The response of FilesApi->init_or_complete_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->init_or_complete_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_name** | **str**| Version name | 

### Return type

[**InitUploadResponse**](InitUploadResponse.md)

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

# **put_file**
> FileUploadResponse put_file(project_name, model_name, version_name)

Upload file contents

Upload file contents

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.file_upload_response import FileUploadResponse
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
    api_instance = mlx.api.model_registry.FilesApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    version_name = 'version_name_example' # str | Version name

    try:
        # Upload file contents
        api_response = api_instance.put_file(project_name, model_name, version_name)
        print("The response of FilesApi->put_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->put_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **version_name** | **str**| Version name | 

### Return type

[**FileUploadResponse**](FileUploadResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Ok |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

