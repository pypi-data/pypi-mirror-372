# revengai.FunctionsThreatScoreApi

All URIs are relative to *https://api.reveng.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_all_function_threat_scores**](FunctionsThreatScoreApi.md#get_all_function_threat_scores) | **GET** /v2/analyses/{analysis_id}/functions/threat_score | Gets the threat score for all functions
[**get_individual_function_threat_score**](FunctionsThreatScoreApi.md#get_individual_function_threat_score) | **GET** /v2/analyses/{analysis_id}/functions/{function_id}/threat_score | Gets the threat score analysis


# **get_all_function_threat_scores**
> BaseResponseFunctionThreatScore get_all_function_threat_scores(analysis_id, authorization=authorization)

Gets the threat score for all functions

Calculates the threat score for all functions inside of an analysis

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_function_threat_score import BaseResponseFunctionThreatScore
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
    api_instance = revengai.FunctionsThreatScoreApi(api_client)
    analysis_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets the threat score for all functions
        api_response = api_instance.get_all_function_threat_scores(analysis_id, authorization=authorization)
        print("The response of FunctionsThreatScoreApi->get_all_function_threat_scores:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsThreatScoreApi->get_all_function_threat_scores: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseFunctionThreatScore**](BaseResponseFunctionThreatScore.md)

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

# **get_individual_function_threat_score**
> BaseResponseFunctionAnalysisThreatScoreData get_individual_function_threat_score(analysis_id, function_id, authorization=authorization)

Gets the threat score analysis

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_function_analysis_threat_score_data import BaseResponseFunctionAnalysisThreatScoreData
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
    api_instance = revengai.FunctionsThreatScoreApi(api_client)
    analysis_id = 56 # int | 
    function_id = 56 # int | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Gets the threat score analysis
        api_response = api_instance.get_individual_function_threat_score(analysis_id, function_id, authorization=authorization)
        print("The response of FunctionsThreatScoreApi->get_individual_function_threat_score:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FunctionsThreatScoreApi->get_individual_function_threat_score: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**|  | 
 **function_id** | **int**|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseFunctionAnalysisThreatScoreData**](BaseResponseFunctionAnalysisThreatScoreData.md)

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

