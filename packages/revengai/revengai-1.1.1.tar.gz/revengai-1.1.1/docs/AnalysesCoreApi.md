# revengai.AnalysesCoreApi

All URIs are relative to *https://api.reveng.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_analysis**](AnalysesCoreApi.md#create_analysis) | **POST** /v2/analyses | Create Analysis
[**delete_analysis**](AnalysesCoreApi.md#delete_analysis) | **DELETE** /v2/analyses/{analysis_id} | Delete Analysis
[**find_similar_functions_batch**](AnalysesCoreApi.md#find_similar_functions_batch) | **POST** /v2/analyses/{analysis_id}/similarity/functions | Batch Symbol ANN using Analysis ID
[**get_analysis_basic_info**](AnalysesCoreApi.md#get_analysis_basic_info) | **GET** /v2/analyses/{analysis_id}/basic | Gets basic analysis information
[**get_analysis_logs**](AnalysesCoreApi.md#get_analysis_logs) | **GET** /v2/analyses/{analysis_id}/logs | Gets the logs of an analysis
[**get_analysis_params**](AnalysesCoreApi.md#get_analysis_params) | **GET** /v2/analyses/{analysis_id}/params | Gets analysis param information
[**get_analysis_status**](AnalysesCoreApi.md#get_analysis_status) | **GET** /v2/analyses/{analysis_id}/status | Gets the status of an analysis
[**get_binary_ann**](AnalysesCoreApi.md#get_binary_ann) | **POST** /v2/binary_ann/{analysis_id} | Binary Ann
[**get_symbol_info_for_binary**](AnalysesCoreApi.md#get_symbol_info_for_binary) | **GET** /v2/analyses/symbol_info/{binary_id} | Gets the symbol information of a binary
[**list_analyses**](AnalysesCoreApi.md#list_analyses) | **GET** /v2/analyses/list | Gets the most recent analyses
[**lookup_binary_id**](AnalysesCoreApi.md#lookup_binary_id) | **GET** /v2/analyses/lookup/{binary_id} | Gets the analysis ID from binary ID
[**requeue_analysis**](AnalysesCoreApi.md#requeue_analysis) | **POST** /v2/analyses/{analysis_id}/requeue | Requeue Analysis
[**update_analysis**](AnalysesCoreApi.md#update_analysis) | **PATCH** /v2/analyses/{analysis_id} | Update Analysis
[**update_analysis_tags**](AnalysesCoreApi.md#update_analysis_tags) | **PATCH** /v2/analyses/{analysis_id}/tags | Update Analysis Tags


# **create_analysis**
> BaseResponseAnalysisCreateResponse create_analysis(analysis_create_request, authorization=authorization)

Create Analysis

Begins an analysis

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.analysis_create_request import AnalysisCreateRequest
from revengai.models.base_response_analysis_create_response import BaseResponseAnalysisCreateResponse
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_create_request = revengai.AnalysisCreateRequest() # AnalysisCreateRequest | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Create Analysis
        api_response = api_instance.create_analysis(analysis_create_request, authorization=authorization)
        print("The response of AnalysesCoreApi->create_analysis:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->create_analysis: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_create_request** | [**AnalysisCreateRequest**](AnalysisCreateRequest.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseAnalysisCreateResponse**](BaseResponseAnalysisCreateResponse.md)

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
**404** | Not Found |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_analysis**
> BaseResponseDict delete_analysis(analysis_id, authorization=authorization)

Delete Analysis

Deletes an analysis based on the provided analysis ID.

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_dict import BaseResponseDict
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Delete Analysis
        api_response = api_instance.delete_analysis(analysis_id, authorization=authorization)
        print("The response of AnalysesCoreApi->delete_analysis:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->delete_analysis: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseDict**](BaseResponseDict.md)

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
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **find_similar_functions_batch**
> BaseResponseNearestNeighborAnalysis find_similar_functions_batch(analysis_id, ann_function, authorization=authorization)

Batch Symbol ANN using Analysis ID

Takes a analysis ID and returns the nearest functions within the database that match those functions

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.ann_function import ANNFunction
from revengai.models.base_response_nearest_neighbor_analysis import BaseResponseNearestNeighborAnalysis
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    ann_function = revengai.ANNFunction() # ANNFunction | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Batch Symbol ANN using Analysis ID
        api_response = api_instance.find_similar_functions_batch(analysis_id, ann_function, authorization=authorization)
        print("The response of AnalysesCoreApi->find_similar_functions_batch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->find_similar_functions_batch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **ann_function** | [**ANNFunction**](ANNFunction.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseNearestNeighborAnalysis**](BaseResponseNearestNeighborAnalysis.md)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_analysis_basic_info**
> BaseResponseBasic get_analysis_basic_info(analysis_id, authorization=authorization)

Gets basic analysis information

Just a random placeholder for now

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_basic import BaseResponseBasic
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets basic analysis information
        api_response = api_instance.get_analysis_basic_info(analysis_id, authorization=authorization)
        print("The response of AnalysesCoreApi->get_analysis_basic_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->get_analysis_basic_info: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseBasic**](BaseResponseBasic.md)

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

# **get_analysis_logs**
> BaseResponseLogs get_analysis_logs(analysis_id, authorization=authorization)

Gets the logs of an analysis

Given an analysis ID gets the current logs of an analysis

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_logs import BaseResponseLogs
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets the logs of an analysis
        api_response = api_instance.get_analysis_logs(analysis_id, authorization=authorization)
        print("The response of AnalysesCoreApi->get_analysis_logs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->get_analysis_logs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseLogs**](BaseResponseLogs.md)

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

# **get_analysis_params**
> BaseResponseParams get_analysis_params(analysis_id, authorization=authorization)

Gets analysis param information

Gets the params that the analysis was run with

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_params import BaseResponseParams
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets analysis param information
        api_response = api_instance.get_analysis_params(analysis_id, authorization=authorization)
        print("The response of AnalysesCoreApi->get_analysis_params:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->get_analysis_params: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseParams**](BaseResponseParams.md)

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

# **get_analysis_status**
> BaseResponseStatus get_analysis_status(analysis_id, authorization=authorization)

Gets the status of an analysis

Given an analysis ID gets the current status of the analysis

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_status import BaseResponseStatus
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets the status of an analysis
        api_response = api_instance.get_analysis_status(analysis_id, authorization=authorization)
        print("The response of AnalysesCoreApi->get_analysis_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->get_analysis_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseStatus**](BaseResponseStatus.md)

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

# **get_binary_ann**
> BaseResponseBinaryAnnListResponse get_binary_ann(analysis_id, binary_ann_form, authorization=authorization)

Binary Ann

Binary Ann

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_binary_ann_list_response import BaseResponseBinaryAnnListResponse
from revengai.models.binary_ann_form import BinaryAnnForm
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    binary_ann_form = revengai.BinaryAnnForm() # BinaryAnnForm | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Binary Ann
        api_response = api_instance.get_binary_ann(analysis_id, binary_ann_form, authorization=authorization)
        print("The response of AnalysesCoreApi->get_binary_ann:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->get_binary_ann: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **binary_ann_form** | [**BinaryAnnForm**](BinaryAnnForm.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseBinaryAnnListResponse**](BaseResponseBinaryAnnListResponse.md)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_symbol_info_for_binary**
> BaseResponseSymbolsInfo get_symbol_info_for_binary(binary_id, authorization=authorization)

Gets the symbol information of a binary

Given a binary ID gets the symbol information of the binary

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_symbols_info import BaseResponseSymbolsInfo
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    binary_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets the symbol information of a binary
        api_response = api_instance.get_symbol_info_for_binary(binary_id, authorization=authorization)
        print("The response of AnalysesCoreApi->get_symbol_info_for_binary:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->get_symbol_info_for_binary: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **binary_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseSymbolsInfo**](BaseResponseSymbolsInfo.md)

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
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_analyses**
> BaseResponseRecent list_analyses(search_term=search_term, workspace=workspace, status=status, model_name=model_name, dynamic_execution_status=dynamic_execution_status, usernames=usernames, limit=limit, offset=offset, order_by=order_by, order=order, authorization=authorization)

Gets the most recent analyses

Gets the most recent analyses provided a scope, this is then paginated, if pages and limit doesnt fit, it increases the limit

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.app_api_rest_v2_analyses_enums_order_by import AppApiRestV2AnalysesEnumsOrderBy
from revengai.models.base_response_recent import BaseResponseRecent
from revengai.models.dynamic_execution_status_input import DynamicExecutionStatusInput
from revengai.models.model_name import ModelName
from revengai.models.order import Order
from revengai.models.status_input import StatusInput
from revengai.models.workspace import Workspace
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    search_term = '' # str |  (optional) (default to '')
    workspace = ["personal"] # List[Workspace] | The workspace to be viewed (optional) (default to ["personal"])
    status = ["All"] # List[StatusInput] | The status of the analysis (optional) (default to ["All"])
    model_name = [revengai.ModelName()] # List[ModelName] | Show analysis belonging to the model (optional)
    dynamic_execution_status = revengai.DynamicExecutionStatusInput() # DynamicExecutionStatusInput | Show analysis that have a dynamic execution with the given status (optional)
    usernames = [] # List[Optional[str]] | Show analysis belonging to the user (optional) (default to [])
    limit = 20 # int |  (optional) (default to 20)
    offset = 0 # int |  (optional) (default to 0)
    order_by = revengai.AppApiRestV2AnalysesEnumsOrderBy() # AppApiRestV2AnalysesEnumsOrderBy |  (optional)
    order = revengai.Order() # Order |  (optional)
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets the most recent analyses
        api_response = api_instance.list_analyses(search_term=search_term, workspace=workspace, status=status, model_name=model_name, dynamic_execution_status=dynamic_execution_status, usernames=usernames, limit=limit, offset=offset, order_by=order_by, order=order, authorization=authorization)
        print("The response of AnalysesCoreApi->list_analyses:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->list_analyses: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_term** | **str**|  | [optional] [default to &#39;&#39;]
 **workspace** | [**List[Workspace]**](Workspace.md)| The workspace to be viewed | [optional] [default to [&quot;personal&quot;]]
 **status** | [**List[StatusInput]**](StatusInput.md)| The status of the analysis | [optional] [default to [&quot;All&quot;]]
 **model_name** | [**List[ModelName]**](ModelName.md)| Show analysis belonging to the model | [optional] 
 **dynamic_execution_status** | [**DynamicExecutionStatusInput**](.md)| Show analysis that have a dynamic execution with the given status | [optional] 
 **usernames** | [**List[Optional[str]]**](str.md)| Show analysis belonging to the user | [optional] [default to []]
 **limit** | **int**|  | [optional] [default to 20]
 **offset** | **int**|  | [optional] [default to 0]
 **order_by** | [**AppApiRestV2AnalysesEnumsOrderBy**](.md)|  | [optional] 
 **order** | [**Order**](.md)|  | [optional] 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseRecent**](BaseResponseRecent.md)

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

# **lookup_binary_id**
> object lookup_binary_id(binary_id, authorization=authorization)

Gets the analysis ID from binary ID

Given an binary ID gets the ID of an analysis

### Example

* Api Key Authentication (APIKey):

```python
import revengai
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    binary_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets the analysis ID from binary ID
        api_response = api_instance.lookup_binary_id(binary_id, authorization=authorization)
        print("The response of AnalysesCoreApi->lookup_binary_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->lookup_binary_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **binary_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

**object**

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

# **requeue_analysis**
> BaseResponseCreated requeue_analysis(analysis_id, re_analysis_form, authorization=authorization)

Requeue Analysis

Re-queues an already uploaded analysis

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_created import BaseResponseCreated
from revengai.models.re_analysis_form import ReAnalysisForm
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    re_analysis_form = revengai.ReAnalysisForm() # ReAnalysisForm | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Requeue Analysis
        api_response = api_instance.requeue_analysis(analysis_id, re_analysis_form, authorization=authorization)
        print("The response of AnalysesCoreApi->requeue_analysis:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->requeue_analysis: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **re_analysis_form** | [**ReAnalysisForm**](ReAnalysisForm.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseCreated**](BaseResponseCreated.md)

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
**404** | Not Found |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_analysis**
> BaseResponseAnalysisDetailResponse update_analysis(analysis_id, analysis_update_request, authorization=authorization)

Update Analysis

Updates analysis attributes (binary_name, analysis_scope). User must be the owner.

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.analysis_update_request import AnalysisUpdateRequest
from revengai.models.base_response_analysis_detail_response import BaseResponseAnalysisDetailResponse
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    analysis_update_request = revengai.AnalysisUpdateRequest() # AnalysisUpdateRequest | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Update Analysis
        api_response = api_instance.update_analysis(analysis_id, analysis_update_request, authorization=authorization)
        print("The response of AnalysesCoreApi->update_analysis:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->update_analysis: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **analysis_update_request** | [**AnalysisUpdateRequest**](AnalysisUpdateRequest.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseAnalysisDetailResponse**](BaseResponseAnalysisDetailResponse.md)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_analysis_tags**
> BaseResponseAnalysisUpdateTagsResponse update_analysis_tags(analysis_id, analysis_update_tags_request, authorization=authorization)

Update Analysis Tags

Updates analysis tags. User must be the owner.

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.analysis_update_tags_request import AnalysisUpdateTagsRequest
from revengai.models.base_response_analysis_update_tags_response import BaseResponseAnalysisUpdateTagsResponse
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
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 56 # int | 
    analysis_update_tags_request = revengai.AnalysisUpdateTagsRequest() # AnalysisUpdateTagsRequest | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Update Analysis Tags
        api_response = api_instance.update_analysis_tags(analysis_id, analysis_update_tags_request, authorization=authorization)
        print("The response of AnalysesCoreApi->update_analysis_tags:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->update_analysis_tags: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **analysis_update_tags_request** | [**AnalysisUpdateTagsRequest**](AnalysisUpdateTagsRequest.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseAnalysisUpdateTagsResponse**](BaseResponseAnalysisUpdateTagsResponse.md)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

