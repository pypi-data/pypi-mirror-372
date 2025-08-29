# revengai.FunctionsDecompilationApi

All URIs are relative to *https://api.reveng.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**check_function_decompilation_task**](FunctionsDecompilationApi.md#check_function_decompilation_task) | **GET** /v2/functions/{function_id}/decompilation/status | Check the status of a function decompilation
[**create_decompilation_comment**](FunctionsDecompilationApi.md#create_decompilation_comment) | **POST** /v2/functions/{function_id}/decompilation/comments | Create a comment for this function
[**create_function_decompilation_task**](FunctionsDecompilationApi.md#create_function_decompilation_task) | **POST** /v2/functions/{function_id}/decompilation | Queues a function decompilation
[**delete_decompilation_comment**](FunctionsDecompilationApi.md#delete_decompilation_comment) | **DELETE** /v2/functions/{function_id}/decompilation/comments/{comment_id} | Delete a comment
[**get_decompilation_comments**](FunctionsDecompilationApi.md#get_decompilation_comments) | **GET** /v2/functions/{function_id}/decompilation/comments | Get comments for this function
[**get_function_decompilation**](FunctionsDecompilationApi.md#get_function_decompilation) | **GET** /v2/functions/{function_id}/decompilation | Get decompilation result
[**update_decompilation_comment**](FunctionsDecompilationApi.md#update_decompilation_comment) | **PATCH** /v2/functions/{function_id}/decompilation/comments/{comment_id} | Update a comment


# **check_function_decompilation_task**
> BaseResponseFunctionTaskResponse check_function_decompilation_task(function_id, authorization=authorization)

Check the status of a function decompilation

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_function_task_response import BaseResponseFunctionTaskResponse
from revengai.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.reveng.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = revengai.Configuration(
    host = "https://api.reveng.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKey
configuration.api_key['APIKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKey'] = 'Bearer'

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.FunctionsDecompilationApi(api_client)
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Check the status of a function decompilation
        api_response = api_instance.check_function_decompilation_task(function_id, authorization=authorization)
        print("The response of FunctionsDecompilationApi->check_function_decompilation_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsDecompilationApi->check_function_decompilation_task: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseFunctionTaskResponse**](BaseResponseFunctionTaskResponse.md)

### Authorization

[APIKey](../README.md#APIKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Invalid request parameters |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_decompilation_comment**
> BaseResponseCommentResponse create_decompilation_comment(function_id, function_comment_create_request, authorization=authorization)

Create a comment for this function

Creates a comment associated with a specified function).

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_comment_response import BaseResponseCommentResponse
from revengai.models.function_comment_create_request import FunctionCommentCreateRequest
from revengai.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.reveng.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = revengai.Configuration(
    host = "https://api.reveng.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKey
configuration.api_key['APIKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKey'] = 'Bearer'

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.FunctionsDecompilationApi(api_client)
    function_id = 56 # int | 
    function_comment_create_request = revengai.FunctionCommentCreateRequest() # FunctionCommentCreateRequest | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Create a comment for this function
        api_response = api_instance.create_decompilation_comment(function_id, function_comment_create_request, authorization=authorization)
        print("The response of FunctionsDecompilationApi->create_decompilation_comment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsDecompilationApi->create_decompilation_comment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **function_comment_create_request** | [**FunctionCommentCreateRequest**](FunctionCommentCreateRequest.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseCommentResponse**](BaseResponseCommentResponse.md)

### Authorization

[APIKey](../README.md#APIKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Invalid request parameters |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_function_decompilation_task**
> BaseResponseStr create_function_decompilation_task(function_id, authorization=authorization)

Queues a function decompilation

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_str import BaseResponseStr
from revengai.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.reveng.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = revengai.Configuration(
    host = "https://api.reveng.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKey
configuration.api_key['APIKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKey'] = 'Bearer'

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.FunctionsDecompilationApi(api_client)
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Queues a function decompilation
        api_response = api_instance.create_function_decompilation_task(function_id, authorization=authorization)
        print("The response of FunctionsDecompilationApi->create_function_decompilation_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsDecompilationApi->create_function_decompilation_task: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseStr**](BaseResponseStr.md)

### Authorization

[APIKey](../README.md#APIKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Invalid request parameters |  -  |
**409** | Security checks already extracted or queued |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_decompilation_comment**
> BaseResponseBool delete_decompilation_comment(comment_id, function_id, authorization=authorization)

Delete a comment

Deletes an existing comment. Users can only delete their own comments.

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_bool import BaseResponseBool
from revengai.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.reveng.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = revengai.Configuration(
    host = "https://api.reveng.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKey
configuration.api_key['APIKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKey'] = 'Bearer'

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.FunctionsDecompilationApi(api_client)
    comment_id = 56 # int | 
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Delete a comment
        api_response = api_instance.delete_decompilation_comment(comment_id, function_id, authorization=authorization)
        print("The response of FunctionsDecompilationApi->delete_decompilation_comment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsDecompilationApi->delete_decompilation_comment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **comment_id** | **int**|  | 
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseBool**](BaseResponseBool.md)

### Authorization

[APIKey](../README.md#APIKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Invalid request parameters |  -  |
**403** | You can only delete your own comments |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_decompilation_comments**
> BaseResponseListCommentResponse get_decompilation_comments(function_id, authorization=authorization)

Get comments for this function

Retrieves all comments created for a specific function. Only returns comments for resources the requesting user has access to.

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_list_comment_response import BaseResponseListCommentResponse
from revengai.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.reveng.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = revengai.Configuration(
    host = "https://api.reveng.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKey
configuration.api_key['APIKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKey'] = 'Bearer'

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.FunctionsDecompilationApi(api_client)
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Get comments for this function
        api_response = api_instance.get_decompilation_comments(function_id, authorization=authorization)
        print("The response of FunctionsDecompilationApi->get_decompilation_comments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsDecompilationApi->get_decompilation_comments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseListCommentResponse**](BaseResponseListCommentResponse.md)

### Authorization

[APIKey](../README.md#APIKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Invalid request parameters |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_function_decompilation**
> BaseResponseDecompilationResponse get_function_decompilation(function_id, authorization=authorization)

Get decompilation result

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_decompilation_response import BaseResponseDecompilationResponse
from revengai.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.reveng.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = revengai.Configuration(
    host = "https://api.reveng.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKey
configuration.api_key['APIKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKey'] = 'Bearer'

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.FunctionsDecompilationApi(api_client)
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Get decompilation result
        api_response = api_instance.get_function_decompilation(function_id, authorization=authorization)
        print("The response of FunctionsDecompilationApi->get_function_decompilation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsDecompilationApi->get_function_decompilation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseDecompilationResponse**](BaseResponseDecompilationResponse.md)

### Authorization

[APIKey](../README.md#APIKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Invalid request parameters |  -  |
**404** | Unable to find a decompilation for the function_id given |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_decompilation_comment**
> BaseResponseCommentResponse update_decompilation_comment(comment_id, function_id, comment_update_request, authorization=authorization)

Update a comment

Updates the content of an existing comment. Users can only update their own comments.

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_comment_response import BaseResponseCommentResponse
from revengai.models.comment_update_request import CommentUpdateRequest
from revengai.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.reveng.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = revengai.Configuration(
    host = "https://api.reveng.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKey
configuration.api_key['APIKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKey'] = 'Bearer'

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.FunctionsDecompilationApi(api_client)
    comment_id = 56 # int | 
    function_id = 56 # int | 
    comment_update_request = revengai.CommentUpdateRequest() # CommentUpdateRequest | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Update a comment
        api_response = api_instance.update_decompilation_comment(comment_id, function_id, comment_update_request, authorization=authorization)
        print("The response of FunctionsDecompilationApi->update_decompilation_comment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsDecompilationApi->update_decompilation_comment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **comment_id** | **int**|  | 
 **function_id** | **int**|  | 
 **comment_update_request** | [**CommentUpdateRequest**](CommentUpdateRequest.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseCommentResponse**](BaseResponseCommentResponse.md)

### Authorization

[APIKey](../README.md#APIKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Invalid request parameters |  -  |
**403** | You can only update your own comments |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

