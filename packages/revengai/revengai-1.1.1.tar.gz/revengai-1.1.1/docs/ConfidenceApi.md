# revengai.ConfidenceApi

All URIs are relative to *https://api.reveng.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_analysis_tag_score**](ConfidenceApi.md#get_analysis_tag_score) | **POST** /v2/confidence/analysis/{analysis_id}/tag_score | Calculate Tag Confidence Score for an Analysis
[**get_analysis_threat_score**](ConfidenceApi.md#get_analysis_threat_score) | **GET** /v2/confidence/analysis/{analysis_id}/threat_score | Calculate Threat Score for Binary
[**get_functions_name_score**](ConfidenceApi.md#get_functions_name_score) | **POST** /v2/confidence/functions/name_score | Calculate function name confidence for a set of Functions
[**get_functions_threat_score**](ConfidenceApi.md#get_functions_threat_score) | **POST** /v2/confidence/functions/threat_score | Calculate Threat Score for a set of Functions


# **get_analysis_tag_score**
> BaseResponseListTagOriginBoxPlotConfidence get_analysis_tag_score(analysis_id, tag_confidence_body, authorization=authorization)

Calculate Tag Confidence Score for an Analysis

Accepts a analysis ID and a list of tags, returns the confidence score for each tag in the list

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_list_tag_origin_box_plot_confidence import BaseResponseListTagOriginBoxPlotConfidence
from revengai.models.tag_confidence_body import TagConfidenceBody
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
    api_instance = revengai.ConfidenceApi(api_client)
    analysis_id = 56 # int | The analysis to calculate the tag scores for
    tag_confidence_body = revengai.TagConfidenceBody() # TagConfidenceBody | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Calculate Tag Confidence Score for an Analysis
        api_response = api_instance.get_analysis_tag_score(analysis_id, tag_confidence_body, authorization=authorization)
        print("The response of ConfidenceApi->get_analysis_tag_score:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfidenceApi->get_analysis_tag_score: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**| The analysis to calculate the tag scores for | 
 **tag_confidence_body** | [**TagConfidenceBody**](TagConfidenceBody.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseListTagOriginBoxPlotConfidence**](BaseResponseListTagOriginBoxPlotConfidence.md)

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

# **get_analysis_threat_score**
> BaseResponseBoxPlotConfidence get_analysis_threat_score(analysis_id, authorization=authorization)

Calculate Threat Score for Binary

Accepts a binary ID and returns the threat score for that binary

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_box_plot_confidence import BaseResponseBoxPlotConfidence
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
    api_instance = revengai.ConfidenceApi(api_client)
    analysis_id = 56 # int | The analysis to calculate the threat score for
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Calculate Threat Score for Binary
        api_response = api_instance.get_analysis_threat_score(analysis_id, authorization=authorization)
        print("The response of ConfidenceApi->get_analysis_threat_score:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfidenceApi->get_analysis_threat_score: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **analysis_id** | **int**| The analysis to calculate the threat score for | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseBoxPlotConfidence**](BaseResponseBoxPlotConfidence.md)

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

# **get_functions_name_score**
> BaseResponseListFunctionBoxPlotConfidence get_functions_name_score(function_name_confidence_body, authorization=authorization)

Calculate function name confidence for a set of Functions

Accepts a list of function ids mapped to a function name, for each function we return a confidence score in that being the correct name for each function. Each function must be from the same model, or you may find some functions missing in the return.

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_list_function_box_plot_confidence import BaseResponseListFunctionBoxPlotConfidence
from revengai.models.function_name_confidence_body import FunctionNameConfidenceBody
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
    api_instance = revengai.ConfidenceApi(api_client)
    function_name_confidence_body = revengai.FunctionNameConfidenceBody() # FunctionNameConfidenceBody | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Calculate function name confidence for a set of Functions
        api_response = api_instance.get_functions_name_score(function_name_confidence_body, authorization=authorization)
        print("The response of ConfidenceApi->get_functions_name_score:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfidenceApi->get_functions_name_score: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **function_name_confidence_body** | [**FunctionNameConfidenceBody**](FunctionNameConfidenceBody.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseListFunctionBoxPlotConfidence**](BaseResponseListFunctionBoxPlotConfidence.md)

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

# **get_functions_threat_score**
> BaseResponseListFunctionBoxPlotConfidence get_functions_threat_score(threat_score_function_body, authorization=authorization)

Calculate Threat Score for a set of Functions

Accepts a list of function ids and returns the threat score for each function. Each function must be from the same model, or you may find some functions missing in the return.

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.base_response_list_function_box_plot_confidence import BaseResponseListFunctionBoxPlotConfidence
from revengai.models.threat_score_function_body import ThreatScoreFunctionBody
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
    api_instance = revengai.ConfidenceApi(api_client)
    threat_score_function_body = revengai.ThreatScoreFunctionBody() # ThreatScoreFunctionBody | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Calculate Threat Score for a set of Functions
        api_response = api_instance.get_functions_threat_score(threat_score_function_body, authorization=authorization)
        print("The response of ConfidenceApi->get_functions_threat_score:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfidenceApi->get_functions_threat_score: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **threat_score_function_body** | [**ThreatScoreFunctionBody**](ThreatScoreFunctionBody.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**BaseResponseListFunctionBoxPlotConfidence**](BaseResponseListFunctionBoxPlotConfidence.md)

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

