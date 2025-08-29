# mlx.api.model_registry.ModelsApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_model**](ModelsApi.md#create_model) | **POST** /projects/{project_name}/models | Create a new model type
[**delete_model**](ModelsApi.md#delete_model) | **DELETE** /projects/{project_name}/models/{model_name} | Delete model and all versions(including files)
[**get_model**](ModelsApi.md#get_model) | **GET** /projects/{project_name}/models/{model_name} | Get model information
[**get_models**](ModelsApi.md#get_models) | **GET** /projects/{project_name}/models | List models in project
[**update_model**](ModelsApi.md#update_model) | **PATCH** /projects/{project_name}/models/{model_name} | Update model information


# **create_model**
> Model create_model(project_name, model_request)

Create a new model type

Create a new model type

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.model import Model
from mlx.api.model_registry.models.model_request import ModelRequest
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
    api_instance = mlx.api.model_registry.ModelsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_request = mlx.api.model_registry.ModelRequest() # ModelRequest | 

    try:
        # Create a new model type
        api_response = api_instance.create_model(project_name, model_request)
        print("The response of ModelsApi->create_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsApi->create_model: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_request** | [**ModelRequest**](ModelRequest.md)|  | 

### Return type

[**Model**](Model.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Created |  -  |
**400** | Bad request |  -  |
**404** | Models not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_model**
> delete_model(project_name, model_name)

Delete model and all versions(including files)

Delete model and all versions(including files)

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
    api_instance = mlx.api.model_registry.ModelsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name

    try:
        # Delete model and all versions(including files)
        api_instance.delete_model(project_name, model_name)
    except Exception as e:
        print("Exception when calling ModelsApi->delete_model: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 

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
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_model**
> Model get_model(project_name, model_name)

Get model information

Get model information

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.model import Model
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
    api_instance = mlx.api.model_registry.ModelsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name

    try:
        # Get model information
        api_response = api_instance.get_model(project_name, model_name)
        print("The response of ModelsApi->get_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsApi->get_model: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 

### Return type

[**Model**](Model.md)

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

# **get_models**
> ModelsResponse get_models(project_name, ascending=ascending, page=page, page_size=page_size, search=search, sort_by=sort_by, tags=tags)

List models in project

List models in project

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
    api_instance = mlx.api.model_registry.ModelsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    ascending = True # bool |  (optional)
    page = 56 # int |  (optional)
    page_size = 56 # int |  (optional)
    search = 'search_example' # str |  (optional)
    sort_by = 'sort_by_example' # str |  (optional)
    tags = ['tags_example'] # List[str] |  (optional)

    try:
        # List models in project
        api_response = api_instance.get_models(project_name, ascending=ascending, page=page, page_size=page_size, search=search, sort_by=sort_by, tags=tags)
        print("The response of ModelsApi->get_models:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsApi->get_models: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
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

# **update_model**
> Model update_model(project_name, model_name, model_update_request)

Update model information

Update model information

### Example

* Bearer (JWT) Authentication (bearerAuth):

```python
import mlx.api.model_registry
from mlx.api.model_registry.models.model import Model
from mlx.api.model_registry.models.model_update_request import ModelUpdateRequest
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
    api_instance = mlx.api.model_registry.ModelsApi(api_client)
    project_name = 'project_name_example' # str | Project name
    model_name = 'model_name_example' # str | Model name
    model_update_request = mlx.api.model_registry.ModelUpdateRequest() # ModelUpdateRequest | 

    try:
        # Update model information
        api_response = api_instance.update_model(project_name, model_name, model_update_request)
        print("The response of ModelsApi->update_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsApi->update_model: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**| Project name | 
 **model_name** | **str**| Model name | 
 **model_update_request** | [**ModelUpdateRequest**](ModelUpdateRequest.md)|  | 

### Return type

[**Model**](Model.md)

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

