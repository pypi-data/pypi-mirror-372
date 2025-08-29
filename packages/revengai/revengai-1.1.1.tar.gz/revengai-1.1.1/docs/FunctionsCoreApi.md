# revengai.FunctionsCoreApi

All URIs are relative to *https://api.reveng.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_analysis_strings**](FunctionsCoreApi.md#get_analysis_strings) | **GET** /v2/analyses/{analysis_id}/functions/strings | Get string information found in the Analysis
[**get_function_blocks**](FunctionsCoreApi.md#get_function_blocks) | **GET** /v2/functions/{function_id}/blocks | Get disassembly blocks related to the function
[**get_function_callees_callers**](FunctionsCoreApi.md#get_function_callees_callers) | **GET** /v2/functions/{function_id}/callees_callers | Get list of functions that call or are called by the specified function
[**get_function_capabilities**](FunctionsCoreApi.md#get_function_capabilities) | **GET** /v2/functions/{function_id}/capabilities | Retrieve a functions capabilities
[**get_function_details**](FunctionsCoreApi.md#get_function_details) | **GET** /v2/functions/{function_id} | Get function details
[**get_function_strings**](FunctionsCoreApi.md#get_function_strings) | **GET** /v2/functions/{function_id}/strings | Get string information found in the function
[**get_similar_functions**](FunctionsCoreApi.md#get_similar_functions) | **GET** /v2/functions/{function_id}/similar-functions | Get list of similar functions


# **get_analysis_strings**
> BaseResponseAnalysisStringsResponse get_analysis_strings(analysis_id, page=page, page_size=page_size, search=search, function_search=function_search, authorization=authorization)

Get string information found in the Analysis

Get string information found in the analysis

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_analysis_strings_response import BaseResponseAnalysisStringsResponse
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
    api_instance = revengai.FunctionsCoreApi(api_client)
    analysis_id = 56 # int | 
    page = 1 # int | The page number to retrieve. (optional) (default to 1)
    page_size = 100 # int | Number of items per page. (optional) (default to 100)
    search = 'search_example' # str | Search is applied to string value (optional)
    function_search = 'function_search_example' # str | Search is applied to function names (optional)
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Get string information found in the Analysis
        api_response = api_instance.get_analysis_strings(analysis_id, page=page, page_size=page_size, search=search, function_search=function_search, authorization=authorization)
        print("The response of FunctionsCoreApi->get_analysis_strings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsCoreApi->get_analysis_strings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **page** | **int**| The page number to retrieve. | [optional] [default to 1]
 **page_size** | **int**| Number of items per page. | [optional] [default to 100]
 **search** | **str**| Search is applied to string value | [optional] 
 **function_search** | **str**| Search is applied to function names | [optional] 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseAnalysisStringsResponse**](BaseResponseAnalysisStringsResponse.md)

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

# **get_function_blocks**
> BaseResponseFunctionBlocksResponse get_function_blocks(function_id, authorization=authorization)

Get disassembly blocks related to the function

Get disassembly blocks related to the function

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_function_blocks_response import BaseResponseFunctionBlocksResponse
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
    api_instance = revengai.FunctionsCoreApi(api_client)
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Get disassembly blocks related to the function
        api_response = api_instance.get_function_blocks(function_id, authorization=authorization)
        print("The response of FunctionsCoreApi->get_function_blocks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsCoreApi->get_function_blocks: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseFunctionBlocksResponse**](BaseResponseFunctionBlocksResponse.md)

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
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_function_callees_callers**
> BaseResponseCalleesCallerFunctionsResponse get_function_callees_callers(function_id, authorization=authorization)

Get list of functions that call or are called by the specified function

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_callees_caller_functions_response import BaseResponseCalleesCallerFunctionsResponse
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
    api_instance = revengai.FunctionsCoreApi(api_client)
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Get list of functions that call or are called by the specified function
        api_response = api_instance.get_function_callees_callers(function_id, authorization=authorization)
        print("The response of FunctionsCoreApi->get_function_callees_callers:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsCoreApi->get_function_callees_callers: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseCalleesCallerFunctionsResponse**](BaseResponseCalleesCallerFunctionsResponse.md)

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

# **get_function_capabilities**
> BaseResponseFunctionCapabilityResponse get_function_capabilities(function_id, authorization=authorization)

Retrieve a functions capabilities

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_function_capability_response import BaseResponseFunctionCapabilityResponse
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
    api_instance = revengai.FunctionsCoreApi(api_client)
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Retrieve a functions capabilities
        api_response = api_instance.get_function_capabilities(function_id, authorization=authorization)
        print("The response of FunctionsCoreApi->get_function_capabilities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsCoreApi->get_function_capabilities: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseFunctionCapabilityResponse**](BaseResponseFunctionCapabilityResponse.md)

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
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_function_details**
> BaseResponseFunctionsDetailResponse get_function_details(function_id, authorization=authorization)

Get function details

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_functions_detail_response import BaseResponseFunctionsDetailResponse
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
    api_instance = revengai.FunctionsCoreApi(api_client)
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Get function details
        api_response = api_instance.get_function_details(function_id, authorization=authorization)
        print("The response of FunctionsCoreApi->get_function_details:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsCoreApi->get_function_details: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseFunctionsDetailResponse**](BaseResponseFunctionsDetailResponse.md)

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

# **get_function_strings**
> BaseResponseFunctionStringsResponse get_function_strings(function_id, page=page, page_size=page_size, search=search, authorization=authorization)

Get string information found in the function

Get string information found in the function

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_function_strings_response import BaseResponseFunctionStringsResponse
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
    api_instance = revengai.FunctionsCoreApi(api_client)
    function_id = 56 # int | 
    page = 1 # int | The page number to retrieve. (optional) (default to 1)
    page_size = 100 # int | Number of items per page. (optional) (default to 100)
    search = 'search_example' # str | Search is applied to string value (optional)
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Get string information found in the function
        api_response = api_instance.get_function_strings(function_id, page=page, page_size=page_size, search=search, authorization=authorization)
        print("The response of FunctionsCoreApi->get_function_strings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsCoreApi->get_function_strings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **page** | **int**| The page number to retrieve. | [optional] [default to 1]
 **page_size** | **int**| Number of items per page. | [optional] [default to 100]
 **search** | **str**| Search is applied to string value | [optional] 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseFunctionStringsResponse**](BaseResponseFunctionStringsResponse.md)

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

# **get_similar_functions**
> BaseResponseListSimilarFunctionsResponse get_similar_functions(function_id, limit=limit, distance=distance, collection_ids=collection_ids, debug=debug, debug_types=debug_types, binary_ids=binary_ids, authorization=authorization)

Get list of similar functions

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_list_similar_functions_response import BaseResponseListSimilarFunctionsResponse
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
    api_instance = revengai.FunctionsCoreApi(api_client)
    function_id = 56 # int | 
    limit = 20 # int | Number of similar functions to return (optional) (default to 20)
    distance = 1.0 # float | Maximum cosine distance (optional) (default to 1.0)
    collection_ids = [] # List[Optional[int]] | Collection filtering by IDs (optional) (default to [])
    debug = False # bool | Only return matching debug functions (optional) (default to False)
    debug_types = ["SYSTEM"] # List[str] | If limiting results to functions with debug names, which type of debug names to include? (optional) (default to ["SYSTEM"])
    binary_ids = [] # List[Optional[int]] | Limit similar functions to specific binaries (optional) (default to [])
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Get list of similar functions
        api_response = api_instance.get_similar_functions(function_id, limit=limit, distance=distance, collection_ids=collection_ids, debug=debug, debug_types=debug_types, binary_ids=binary_ids, authorization=authorization)
        print("The response of FunctionsCoreApi->get_similar_functions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsCoreApi->get_similar_functions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_id** | **int**|  | 
 **limit** | **int**| Number of similar functions to return | [optional] [default to 20]
 **distance** | **float**| Maximum cosine distance | [optional] [default to 1.0]
 **collection_ids** | [**List[Optional[int]]**](int.md)| Collection filtering by IDs | [optional] [default to []]
 **debug** | **bool**| Only return matching debug functions | [optional] [default to False]
 **debug_types** | [**List[str]**](str.md)| If limiting results to functions with debug names, which type of debug names to include? | [optional] [default to [&quot;SYSTEM&quot;]]
 **binary_ids** | [**List[Optional[int]]**](int.md)| Limit similar functions to specific binaries | [optional] [default to []]
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseListSimilarFunctionsResponse**](BaseResponseListSimilarFunctionsResponse.md)

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

