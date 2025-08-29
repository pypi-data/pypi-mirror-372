# revengai

This is the Python SDK for the RevEng.AI API.

To use the SDK you will first need to obtain an API key from [https://reveng.ai](https://reveng.ai/register).

## Installation
Once you have the API key you can install the SDK via pip:
```bash
pip install revengai
```

## Usage

The following is an example of how to use the SDK to get the logs of an analysis:

```python
import os
import revengai

configuration = revengai.Configuration(api_key={'APIKey': os.environ["API_KEY"]})

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.AnalysesCoreApi(api_client)
    analysis_id = 715320

    try:
        # Gets the logs of an analysis
        api_response = api_instance.get_analysis_logs(analysis_id)
        print("The response of AnalysesCoreApi->get_analysis_logs:\n")
        print(api_response)
    except Exception as e:
        print("Exception when calling AnalysesCoreApi->get_analysis_logs: %s\n" % e)
```

## Documentation for API Endpoints

All URIs are relative to *https://api.reveng.ai*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AnalysesCommentsApi* | [**create_analysis_comment**](docs/AnalysesCommentsApi.md#create_analysis_comment) | **POST** /v2/analyses/{analysis_id}/comments | Create a comment for this analysis
*AnalysesCommentsApi* | [**delete_analysis_comment**](docs/AnalysesCommentsApi.md#delete_analysis_comment) | **DELETE** /v2/analyses/{analysis_id}/comments/{comment_id} | Delete a comment
*AnalysesCommentsApi* | [**get_analysis_comments**](docs/AnalysesCommentsApi.md#get_analysis_comments) | **GET** /v2/analyses/{analysis_id}/comments | Get comments for this analysis
*AnalysesCommentsApi* | [**update_analysis_comment**](docs/AnalysesCommentsApi.md#update_analysis_comment) | **PATCH** /v2/analyses/{analysis_id}/comments/{comment_id} | Update a comment
*AnalysesCoreApi* | [**create_analysis**](docs/AnalysesCoreApi.md#create_analysis) | **POST** /v2/analyses | Create Analysis
*AnalysesCoreApi* | [**delete_analysis**](docs/AnalysesCoreApi.md#delete_analysis) | **DELETE** /v2/analyses/{analysis_id} | Delete Analysis
*AnalysesCoreApi* | [**find_similar_functions_batch**](docs/AnalysesCoreApi.md#find_similar_functions_batch) | **POST** /v2/analyses/{analysis_id}/similarity/functions | Batch Symbol ANN using Analysis ID
*AnalysesCoreApi* | [**get_analysis_basic_info**](docs/AnalysesCoreApi.md#get_analysis_basic_info) | **GET** /v2/analyses/{analysis_id}/basic | Gets basic analysis information
*AnalysesCoreApi* | [**get_analysis_logs**](docs/AnalysesCoreApi.md#get_analysis_logs) | **GET** /v2/analyses/{analysis_id}/logs | Gets the logs of an analysis
*AnalysesCoreApi* | [**get_analysis_params**](docs/AnalysesCoreApi.md#get_analysis_params) | **GET** /v2/analyses/{analysis_id}/params | Gets analysis param information
*AnalysesCoreApi* | [**get_analysis_status**](docs/AnalysesCoreApi.md#get_analysis_status) | **GET** /v2/analyses/{analysis_id}/status | Gets the status of an analysis
*AnalysesCoreApi* | [**get_binary_ann**](docs/AnalysesCoreApi.md#get_binary_ann) | **POST** /v2/binary_ann/{analysis_id} | Binary Ann
*AnalysesCoreApi* | [**get_symbol_info_for_binary**](docs/AnalysesCoreApi.md#get_symbol_info_for_binary) | **GET** /v2/analyses/symbol_info/{binary_id} | Gets the symbol information of a binary
*AnalysesCoreApi* | [**list_analyses**](docs/AnalysesCoreApi.md#list_analyses) | **GET** /v2/analyses/list | Gets the most recent analyses
*AnalysesCoreApi* | [**lookup_binary_id**](docs/AnalysesCoreApi.md#lookup_binary_id) | **GET** /v2/analyses/lookup/{binary_id} | Gets the analysis ID from binary ID
*AnalysesCoreApi* | [**requeue_analysis**](docs/AnalysesCoreApi.md#requeue_analysis) | **POST** /v2/analyses/{analysis_id}/requeue | Requeue Analysis
*AnalysesCoreApi* | [**update_analysis**](docs/AnalysesCoreApi.md#update_analysis) | **PATCH** /v2/analyses/{analysis_id} | Update Analysis
*AnalysesCoreApi* | [**update_analysis_tags**](docs/AnalysesCoreApi.md#update_analysis_tags) | **PATCH** /v2/analyses/{analysis_id}/tags | Update Analysis Tags
*AnalysesDynamicExecutionApi* | [**get_dynamic_execution_status**](docs/AnalysesDynamicExecutionApi.md#get_dynamic_execution_status) | **GET** /v2/analyses/{analysis_id}/dynamic-execution/status | Get the status of a dynamic execution task
*AnalysesDynamicExecutionApi* | [**get_network_overview**](docs/AnalysesDynamicExecutionApi.md#get_network_overview) | **GET** /v2/analyses/{analysis_id}/dynamic-execution/network-overview | Get the dynamic execution results for network overview
*AnalysesDynamicExecutionApi* | [**get_process_dump**](docs/AnalysesDynamicExecutionApi.md#get_process_dump) | **GET** /v2/analyses/{analysis_id}/dynamic-execution/process-dumps/{dump_name} | Get the dynamic execution results for a specific process dump
*AnalysesDynamicExecutionApi* | [**get_process_dumps**](docs/AnalysesDynamicExecutionApi.md#get_process_dumps) | **GET** /v2/analyses/{analysis_id}/dynamic-execution/process-dumps | Get the dynamic execution results for process dumps
*AnalysesDynamicExecutionApi* | [**get_process_registry**](docs/AnalysesDynamicExecutionApi.md#get_process_registry) | **GET** /v2/analyses/{analysis_id}/dynamic-execution/process-registry | Get the dynamic execution results for process registry
*AnalysesDynamicExecutionApi* | [**get_process_tree**](docs/AnalysesDynamicExecutionApi.md#get_process_tree) | **GET** /v2/analyses/{analysis_id}/dynamic-execution/process-tree | Get the dynamic execution results for process tree
*AnalysesDynamicExecutionApi* | [**get_ttps**](docs/AnalysesDynamicExecutionApi.md#get_ttps) | **GET** /v2/analyses/{analysis_id}/dynamic-execution/ttps | Get the dynamic execution results for ttps
*AnalysesResultsMetadataApi* | [**get_capabilities**](docs/AnalysesResultsMetadataApi.md#get_capabilities) | **GET** /v2/analyses/{analysis_id}/capabilities | Gets the capabilities from the analysis
*AnalysesResultsMetadataApi* | [**get_communities**](docs/AnalysesResultsMetadataApi.md#get_communities) | **GET** /v2/analyses/{analysis_id}/communities | Gets the communities found in the analysis
*AnalysesResultsMetadataApi* | [**get_functions_list**](docs/AnalysesResultsMetadataApi.md#get_functions_list) | **GET** /v2/analyses/{analysis_id}/functions/list | Gets functions from analysis
*AnalysesResultsMetadataApi* | [**get_pdf**](docs/AnalysesResultsMetadataApi.md#get_pdf) | **GET** /v2/analyses/{analysis_id}/pdf | Gets the PDF found in the analysis
*AnalysesResultsMetadataApi* | [**get_sbom**](docs/AnalysesResultsMetadataApi.md#get_sbom) | **GET** /v2/analyses/{analysis_id}/sbom | Gets the software-bill-of-materials (SBOM) found in the analysis
*AnalysesResultsMetadataApi* | [**get_tags**](docs/AnalysesResultsMetadataApi.md#get_tags) | **GET** /v2/analyses/{analysis_id}/tags | Get function tags with maliciousness score
*AnalysesResultsMetadataApi* | [**get_threat_score**](docs/AnalysesResultsMetadataApi.md#get_threat_score) | **GET** /v2/analyses/{analysis_id}/threat_score | Gets the threat score found in the analysis
*AnalysesResultsMetadataApi* | [**get_vulnerabilities**](docs/AnalysesResultsMetadataApi.md#get_vulnerabilities) | **GET** /v2/analyses/{analysis_id}/vulnerabilities | Gets the vulnerabilities found in the analysis
*AnalysesSecurityChecksApi* | [**create_scurity_checks_task**](docs/AnalysesSecurityChecksApi.md#create_scurity_checks_task) | **POST** /v2/analyses/{analysis_id}/security-checks | Queues a security check process
*AnalysesSecurityChecksApi* | [**get_security_checks**](docs/AnalysesSecurityChecksApi.md#get_security_checks) | **GET** /v2/analyses/{analysis_id}/security-checks | Get Security Checks
*AnalysesSecurityChecksApi* | [**get_security_checks_task_status**](docs/AnalysesSecurityChecksApi.md#get_security_checks_task_status) | **GET** /v2/analyses/{analysis_id}/security-checks/status | Check the status of a security check process
*AuthenticationUsersApi* | [**get_requester_user_info**](docs/AuthenticationUsersApi.md#get_requester_user_info) | **GET** /v2/users/me | Get the requesters user information
*AuthenticationUsersApi* | [**get_user**](docs/AuthenticationUsersApi.md#get_user) | **GET** /v2/users/{user_id} | Get a user&#39;s public information
*AuthenticationUsersApi* | [**get_user_activity**](docs/AuthenticationUsersApi.md#get_user_activity) | **GET** /v2/users/activity | Get auth user activity
*AuthenticationUsersApi* | [**get_user_comments**](docs/AuthenticationUsersApi.md#get_user_comments) | **GET** /v2/users/me/comments | Get comments by user
*AuthenticationUsersApi* | [**login_user**](docs/AuthenticationUsersApi.md#login_user) | **POST** /v2/auth/login | Authenticate a user
*BinariesApi* | [**download_zipped_binary**](docs/BinariesApi.md#download_zipped_binary) | **GET** /v2/binaries/{binary_id}/download-zipped | Downloads a zipped binary with password protection
*BinariesApi* | [**get_binary_additional_details**](docs/BinariesApi.md#get_binary_additional_details) | **GET** /v2/binaries/{binary_id}/additional-details | Gets the additional details of a binary
*BinariesApi* | [**get_binary_details**](docs/BinariesApi.md#get_binary_details) | **GET** /v2/binaries/{binary_id}/details | Gets the details of a binary
*BinariesApi* | [**get_binary_die_info**](docs/BinariesApi.md#get_binary_die_info) | **GET** /v2/binaries/{binary_id}/die-info | Gets the die info of a binary
*BinariesApi* | [**get_binary_externals**](docs/BinariesApi.md#get_binary_externals) | **GET** /v2/binaries/{binary_id}/externals | Gets the external details of a binary
*BinariesApi* | [**get_related_binaries**](docs/BinariesApi.md#get_related_binaries) | **GET** /v2/binaries/{binary_id}/related | Gets the related binaries of a binary.
*CollectionsApi* | [**create_collection**](docs/CollectionsApi.md#create_collection) | **POST** /v2/collections | Creates new collection information
*CollectionsApi* | [**delete_collection**](docs/CollectionsApi.md#delete_collection) | **DELETE** /v2/collections/{collection_id} | Deletes a collection
*CollectionsApi* | [**get_collection**](docs/CollectionsApi.md#get_collection) | **GET** /v2/collections/{collection_id} | Returns a collection
*CollectionsApi* | [**list_collections**](docs/CollectionsApi.md#list_collections) | **GET** /v2/collections | Gets basic collections information
*CollectionsApi* | [**update_collection**](docs/CollectionsApi.md#update_collection) | **PATCH** /v2/collections/{collection_id} | Updates a collection
*CollectionsApi* | [**update_collection_binaries**](docs/CollectionsApi.md#update_collection_binaries) | **PATCH** /v2/collections/{collection_id}/binaries | Updates a collection binaries
*CollectionsApi* | [**update_collection_tags**](docs/CollectionsApi.md#update_collection_tags) | **PATCH** /v2/collections/{collection_id}/tags | Updates a collection tags
*ConfidenceApi* | [**get_analysis_tag_score**](docs/ConfidenceApi.md#get_analysis_tag_score) | **POST** /v2/confidence/analysis/{analysis_id}/tag_score | Calculate Tag Confidence Score for an Analysis
*ConfidenceApi* | [**get_analysis_threat_score**](docs/ConfidenceApi.md#get_analysis_threat_score) | **GET** /v2/confidence/analysis/{analysis_id}/threat_score | Calculate Threat Score for Binary
*ConfidenceApi* | [**get_functions_name_score**](docs/ConfidenceApi.md#get_functions_name_score) | **POST** /v2/confidence/functions/name_score | Calculate function name confidence for a set of Functions
*ConfidenceApi* | [**get_functions_threat_score**](docs/ConfidenceApi.md#get_functions_threat_score) | **POST** /v2/confidence/functions/threat_score | Calculate Threat Score for a set of Functions
*ExternalSourcesApi* | [**create_external_task_mb**](docs/ExternalSourcesApi.md#create_external_task_mb) | **POST** /v2/analysis/{analysis_id}/external/mb | Pulls data from VirusTotal
*ExternalSourcesApi* | [**create_external_task_vt**](docs/ExternalSourcesApi.md#create_external_task_vt) | **POST** /v2/analysis/{analysis_id}/external/vt | Pulls data from VirusTotal
*ExternalSourcesApi* | [**get_mb_data**](docs/ExternalSourcesApi.md#get_mb_data) | **GET** /v2/analysis/{analysis_id}/external/mb | Get MalwareBazaar data
*ExternalSourcesApi* | [**get_mb_task_status**](docs/ExternalSourcesApi.md#get_mb_task_status) | **GET** /v2/analysis/{analysis_id}/external/mb/status | Check the status of MalwareBazaar data retrieval
*ExternalSourcesApi* | [**get_vt_data**](docs/ExternalSourcesApi.md#get_vt_data) | **GET** /v2/analysis/{analysis_id}/external/vt | Get VirusTotal data
*ExternalSourcesApi* | [**get_vt_task_status**](docs/ExternalSourcesApi.md#get_vt_task_status) | **GET** /v2/analysis/{analysis_id}/external/vt/status | Check the status of VirusTotal data retrieval
*FirmwareApi* | [**get_binaries_for_firmware_task**](docs/FirmwareApi.md#get_binaries_for_firmware_task) | **GET** /v2/firmware/get-binaries/{task_id} | Upload firmware for unpacking
*FirmwareApi* | [**upload_firmware**](docs/FirmwareApi.md#upload_firmware) | **POST** /v2/firmware | Upload firmware for unpacking
*FunctionsAIDecompilationApi* | [**create_ai_decompilation_comment**](docs/FunctionsAIDecompilationApi.md#create_ai_decompilation_comment) | **POST** /v2/functions/{function_id}/ai-decompilation/comments | Create a comment for this function
*FunctionsAIDecompilationApi* | [**create_ai_decompilation_task**](docs/FunctionsAIDecompilationApi.md#create_ai_decompilation_task) | **POST** /v2/functions/{function_id}/ai-decompilation | Begins AI Decompilation Process
*FunctionsAIDecompilationApi* | [**delete_ai_decompilation_comment**](docs/FunctionsAIDecompilationApi.md#delete_ai_decompilation_comment) | **DELETE** /v2/functions/{function_id}/ai-decompilation/comments/{comment_id} | Delete a comment
*FunctionsAIDecompilationApi* | [**get_ai_decompilation_comments**](docs/FunctionsAIDecompilationApi.md#get_ai_decompilation_comments) | **GET** /v2/functions/{function_id}/ai-decompilation/comments | Get comments for this function
*FunctionsAIDecompilationApi* | [**get_ai_decompilation_rating**](docs/FunctionsAIDecompilationApi.md#get_ai_decompilation_rating) | **GET** /v2/functions/{function_id}/ai-decompilation/rating | Get rating for AI decompilation
*FunctionsAIDecompilationApi* | [**get_ai_decompilation_task_result**](docs/FunctionsAIDecompilationApi.md#get_ai_decompilation_task_result) | **GET** /v2/functions/{function_id}/ai-decompilation | Polls AI Decompilation Process
*FunctionsAIDecompilationApi* | [**get_ai_decompilation_task_status**](docs/FunctionsAIDecompilationApi.md#get_ai_decompilation_task_status) | **GET** /v2/functions/{function_id}/ai-decompilation/status | Check the status of a function ai decompilation
*FunctionsAIDecompilationApi* | [**update_ai_decompilation_comment**](docs/FunctionsAIDecompilationApi.md#update_ai_decompilation_comment) | **PATCH** /v2/functions/{function_id}/ai-decompilation/comments/{comment_id} | Update a comment
*FunctionsAIDecompilationApi* | [**upsert_ai_decompilation_rating**](docs/FunctionsAIDecompilationApi.md#upsert_ai_decompilation_rating) | **PATCH** /v2/functions/{function_id}/ai-decompilation/rating | Upsert rating for AI decompilation
*FunctionsBlockCommentsApi* | [**generate_block_comments_for_block_in_function**](docs/FunctionsBlockCommentsApi.md#generate_block_comments_for_block_in_function) | **POST** /v2/functions/{function_id}/block-comments/single | Generate block comments for a specific block in a function
*FunctionsBlockCommentsApi* | [**generate_block_comments_for_function**](docs/FunctionsBlockCommentsApi.md#generate_block_comments_for_function) | **POST** /v2/functions/{function_id}/block-comments | Generate block comments for a function
*FunctionsBlockCommentsApi* | [**generate_overview_comment_for_function**](docs/FunctionsBlockCommentsApi.md#generate_overview_comment_for_function) | **POST** /v2/functions/{function_id}/block-comments/overview | Generate overview comment for a function
*FunctionsCoreApi* | [**get_analysis_strings**](docs/FunctionsCoreApi.md#get_analysis_strings) | **GET** /v2/analyses/{analysis_id}/functions/strings | Get string information found in the Analysis
*FunctionsCoreApi* | [**get_function_blocks**](docs/FunctionsCoreApi.md#get_function_blocks) | **GET** /v2/functions/{function_id}/blocks | Get disassembly blocks related to the function
*FunctionsCoreApi* | [**get_function_callees_callers**](docs/FunctionsCoreApi.md#get_function_callees_callers) | **GET** /v2/functions/{function_id}/callees_callers | Get list of functions that call or are called by the specified function
*FunctionsCoreApi* | [**get_function_capabilities**](docs/FunctionsCoreApi.md#get_function_capabilities) | **GET** /v2/functions/{function_id}/capabilities | Retrieve a functions capabilities
*FunctionsCoreApi* | [**get_function_details**](docs/FunctionsCoreApi.md#get_function_details) | **GET** /v2/functions/{function_id} | Get function details
*FunctionsCoreApi* | [**get_function_strings**](docs/FunctionsCoreApi.md#get_function_strings) | **GET** /v2/functions/{function_id}/strings | Get string information found in the function
*FunctionsCoreApi* | [**get_similar_functions**](docs/FunctionsCoreApi.md#get_similar_functions) | **GET** /v2/functions/{function_id}/similar-functions | Get list of similar functions
*FunctionsDataTypesApi* | [**generate_function_data_types_for_analysis**](docs/FunctionsDataTypesApi.md#generate_function_data_types_for_analysis) | **POST** /v2/analyses/{analysis_id}/functions/data_types | Generate Function Data Types
*FunctionsDataTypesApi* | [**generate_function_data_types_for_functions**](docs/FunctionsDataTypesApi.md#generate_function_data_types_for_functions) | **POST** /v2/functions/data_types | Generate Function Data Types for an arbitrary list of functions
*FunctionsDataTypesApi* | [**get_function_data_types**](docs/FunctionsDataTypesApi.md#get_function_data_types) | **GET** /v2/analyses/{analysis_id}/functions/{function_id}/data_types | Get Function Data Types
*FunctionsDataTypesApi* | [**list_function_data_types_for_analysis**](docs/FunctionsDataTypesApi.md#list_function_data_types_for_analysis) | **GET** /v2/analyses/{analysis_id}/functions/data_types | List Function Data Types
*FunctionsDataTypesApi* | [**list_function_data_types_for_functions**](docs/FunctionsDataTypesApi.md#list_function_data_types_for_functions) | **GET** /v2/functions/data_types | List Function Data Types
*FunctionsDataTypesApi* | [**update_function_data_types**](docs/FunctionsDataTypesApi.md#update_function_data_types) | **PUT** /v2/analyses/{analysis_id}/functions/{function_id}/data_types | Update Function Data Types
*FunctionsDecompilationApi* | [**check_function_decompilation_task**](docs/FunctionsDecompilationApi.md#check_function_decompilation_task) | **GET** /v2/functions/{function_id}/decompilation/status | Check the status of a function decompilation
*FunctionsDecompilationApi* | [**create_decompilation_comment**](docs/FunctionsDecompilationApi.md#create_decompilation_comment) | **POST** /v2/functions/{function_id}/decompilation/comments | Create a comment for this function
*FunctionsDecompilationApi* | [**create_function_decompilation_task**](docs/FunctionsDecompilationApi.md#create_function_decompilation_task) | **POST** /v2/functions/{function_id}/decompilation | Queues a function decompilation
*FunctionsDecompilationApi* | [**delete_decompilation_comment**](docs/FunctionsDecompilationApi.md#delete_decompilation_comment) | **DELETE** /v2/functions/{function_id}/decompilation/comments/{comment_id} | Delete a comment
*FunctionsDecompilationApi* | [**get_decompilation_comments**](docs/FunctionsDecompilationApi.md#get_decompilation_comments) | **GET** /v2/functions/{function_id}/decompilation/comments | Get comments for this function
*FunctionsDecompilationApi* | [**get_function_decompilation**](docs/FunctionsDecompilationApi.md#get_function_decompilation) | **GET** /v2/functions/{function_id}/decompilation | Get decompilation result
*FunctionsDecompilationApi* | [**update_decompilation_comment**](docs/FunctionsDecompilationApi.md#update_decompilation_comment) | **PATCH** /v2/functions/{function_id}/decompilation/comments/{comment_id} | Update a comment
*FunctionsRenamingHistoryApi* | [**batch_rename_function**](docs/FunctionsRenamingHistoryApi.md#batch_rename_function) | **POST** /v2/functions/rename/batch | Batch Rename Functions
*FunctionsRenamingHistoryApi* | [**get_function_name_history**](docs/FunctionsRenamingHistoryApi.md#get_function_name_history) | **GET** /v2/functions/history/{function_id} | Get Function Name History
*FunctionsRenamingHistoryApi* | [**rename_function_id**](docs/FunctionsRenamingHistoryApi.md#rename_function_id) | **POST** /v2/functions/rename/{function_id} | Rename Function
*FunctionsRenamingHistoryApi* | [**revert_function_name**](docs/FunctionsRenamingHistoryApi.md#revert_function_name) | **POST** /v2/functions/history/{function_id}/{history_id} | Revert the function name
*FunctionsThreatScoreApi* | [**get_all_function_threat_scores**](docs/FunctionsThreatScoreApi.md#get_all_function_threat_scores) | **GET** /v2/analyses/{analysis_id}/functions/threat_score | Gets the threat score for all functions
*FunctionsThreatScoreApi* | [**get_individual_function_threat_score**](docs/FunctionsThreatScoreApi.md#get_individual_function_threat_score) | **GET** /v2/analyses/{analysis_id}/functions/{function_id}/threat_score | Gets the threat score analysis
*ModelsApi* | [**get_models**](docs/ModelsApi.md#get_models) | **GET** /v2/models | Gets models
*SearchApi* | [**search_binaries**](docs/SearchApi.md#search_binaries) | **GET** /v2/search/binaries | Binaries search
*SearchApi* | [**search_collections**](docs/SearchApi.md#search_collections) | **GET** /v2/search/collections | Collections search
*SearchApi* | [**search_functions**](docs/SearchApi.md#search_functions) | **GET** /v2/search/functions | Functions search
*SearchApi* | [**search_tags**](docs/SearchApi.md#search_tags) | **GET** /v2/search/tags | Tags search


## Documentation For Models

 - [ANNFunction](docs/ANNFunction.md)
 - [Addr](docs/Addr.md)
 - [AiDecompilationRating](docs/AiDecompilationRating.md)
 - [AnalysisAccessInfo](docs/AnalysisAccessInfo.md)
 - [AnalysisConfig](docs/AnalysisConfig.md)
 - [AnalysisCreateRequest](docs/AnalysisCreateRequest.md)
 - [AnalysisCreateResponse](docs/AnalysisCreateResponse.md)
 - [AnalysisDetailResponse](docs/AnalysisDetailResponse.md)
 - [AnalysisFunctions](docs/AnalysisFunctions.md)
 - [AnalysisRecord](docs/AnalysisRecord.md)
 - [AnalysisScope](docs/AnalysisScope.md)
 - [AnalysisStringsResponse](docs/AnalysisStringsResponse.md)
 - [AnalysisThreatScoreData](docs/AnalysisThreatScoreData.md)
 - [AnalysisUpdateRequest](docs/AnalysisUpdateRequest.md)
 - [AnalysisUpdateTagsRequest](docs/AnalysisUpdateTagsRequest.md)
 - [AnalysisUpdateTagsResponse](docs/AnalysisUpdateTagsResponse.md)
 - [AppApiRestV2AnalysesEnumsDynamicExecutionStatus](docs/AppApiRestV2AnalysesEnumsDynamicExecutionStatus.md)
 - [AppApiRestV2AnalysesEnumsOrderBy](docs/AppApiRestV2AnalysesEnumsOrderBy.md)
 - [AppApiRestV2AnalysesResponsesAnalysisTags](docs/AppApiRestV2AnalysesResponsesAnalysisTags.md)
 - [AppApiRestV2AnalysesResponsesTagItem](docs/AppApiRestV2AnalysesResponsesTagItem.md)
 - [AppApiRestV2CollectionsEnumsOrderBy](docs/AppApiRestV2CollectionsEnumsOrderBy.md)
 - [AppApiRestV2FunctionsResponsesFunction](docs/AppApiRestV2FunctionsResponsesFunction.md)
 - [AppApiRestV2FunctionsTypesFunction](docs/AppApiRestV2FunctionsTypesFunction.md)
 - [AppApiRestV2InfoResponsesAnalysisTags](docs/AppApiRestV2InfoResponsesAnalysisTags.md)
 - [AppCoreResponsesBaseBaseResponseAnalysisTags1](docs/AppCoreResponsesBaseBaseResponseAnalysisTags1.md)
 - [AppCoreResponsesBaseBaseResponseAnalysisTags2](docs/AppCoreResponsesBaseBaseResponseAnalysisTags2.md)
 - [AppServicesBinaryAnnSchemaTagItem](docs/AppServicesBinaryAnnSchemaTagItem.md)
 - [AppServicesDynamicExecutionSchemasDynamicExecutionStatus](docs/AppServicesDynamicExecutionSchemasDynamicExecutionStatus.md)
 - [Argument](docs/Argument.md)
 - [BaseResponse](docs/BaseResponse.md)
 - [BaseResponseAnalysisCreateResponse](docs/BaseResponseAnalysisCreateResponse.md)
 - [BaseResponseAnalysisDetailResponse](docs/BaseResponseAnalysisDetailResponse.md)
 - [BaseResponseAnalysisFunctions](docs/BaseResponseAnalysisFunctions.md)
 - [BaseResponseAnalysisStringsResponse](docs/BaseResponseAnalysisStringsResponse.md)
 - [BaseResponseAnalysisThreatScoreData](docs/BaseResponseAnalysisThreatScoreData.md)
 - [BaseResponseAnalysisUpdateTagsResponse](docs/BaseResponseAnalysisUpdateTagsResponse.md)
 - [BaseResponseBasic](docs/BaseResponseBasic.md)
 - [BaseResponseBinaryAdditionalResponse](docs/BaseResponseBinaryAdditionalResponse.md)
 - [BaseResponseBinaryAnnListResponse](docs/BaseResponseBinaryAnnListResponse.md)
 - [BaseResponseBinaryDetailsResponse](docs/BaseResponseBinaryDetailsResponse.md)
 - [BaseResponseBinaryExternalsResponse](docs/BaseResponseBinaryExternalsResponse.md)
 - [BaseResponseBinarySearchResponse](docs/BaseResponseBinarySearchResponse.md)
 - [BaseResponseBlockCommentsGenerationForFunctionResponse](docs/BaseResponseBlockCommentsGenerationForFunctionResponse.md)
 - [BaseResponseBlockCommentsOverviewGenerationResponse](docs/BaseResponseBlockCommentsOverviewGenerationResponse.md)
 - [BaseResponseBool](docs/BaseResponseBool.md)
 - [BaseResponseBoxPlotConfidence](docs/BaseResponseBoxPlotConfidence.md)
 - [BaseResponseCalleesCallerFunctionsResponse](docs/BaseResponseCalleesCallerFunctionsResponse.md)
 - [BaseResponseCapabilities](docs/BaseResponseCapabilities.md)
 - [BaseResponseCheckSecurityChecksTaskResponse](docs/BaseResponseCheckSecurityChecksTaskResponse.md)
 - [BaseResponseChildBinariesResponse](docs/BaseResponseChildBinariesResponse.md)
 - [BaseResponseCollectionBinariesUpdateResponse](docs/BaseResponseCollectionBinariesUpdateResponse.md)
 - [BaseResponseCollectionResponse](docs/BaseResponseCollectionResponse.md)
 - [BaseResponseCollectionSearchResponse](docs/BaseResponseCollectionSearchResponse.md)
 - [BaseResponseCollectionTagsUpdateResponse](docs/BaseResponseCollectionTagsUpdateResponse.md)
 - [BaseResponseCommentResponse](docs/BaseResponseCommentResponse.md)
 - [BaseResponseCommunities](docs/BaseResponseCommunities.md)
 - [BaseResponseCreated](docs/BaseResponseCreated.md)
 - [BaseResponseDecompilationResponse](docs/BaseResponseDecompilationResponse.md)
 - [BaseResponseDict](docs/BaseResponseDict.md)
 - [BaseResponseDynamicExecutionStatus](docs/BaseResponseDynamicExecutionStatus.md)
 - [BaseResponseExternalResponse](docs/BaseResponseExternalResponse.md)
 - [BaseResponseFunctionAnalysisThreatScoreData](docs/BaseResponseFunctionAnalysisThreatScoreData.md)
 - [BaseResponseFunctionBlocksResponse](docs/BaseResponseFunctionBlocksResponse.md)
 - [BaseResponseFunctionCapabilityResponse](docs/BaseResponseFunctionCapabilityResponse.md)
 - [BaseResponseFunctionDataTypes](docs/BaseResponseFunctionDataTypes.md)
 - [BaseResponseFunctionDataTypesList](docs/BaseResponseFunctionDataTypesList.md)
 - [BaseResponseFunctionSearchResponse](docs/BaseResponseFunctionSearchResponse.md)
 - [BaseResponseFunctionStringsResponse](docs/BaseResponseFunctionStringsResponse.md)
 - [BaseResponseFunctionTaskResponse](docs/BaseResponseFunctionTaskResponse.md)
 - [BaseResponseFunctionThreatScore](docs/BaseResponseFunctionThreatScore.md)
 - [BaseResponseFunctionsDetailResponse](docs/BaseResponseFunctionsDetailResponse.md)
 - [BaseResponseGenerateFunctionDataTypes](docs/BaseResponseGenerateFunctionDataTypes.md)
 - [BaseResponseGenerationStatusList](docs/BaseResponseGenerationStatusList.md)
 - [BaseResponseGetAiDecompilationRatingResponse](docs/BaseResponseGetAiDecompilationRatingResponse.md)
 - [BaseResponseGetAiDecompilationTask](docs/BaseResponseGetAiDecompilationTask.md)
 - [BaseResponseGetPublicUserResponse](docs/BaseResponseGetPublicUserResponse.md)
 - [BaseResponseGetUserResponse](docs/BaseResponseGetUserResponse.md)
 - [BaseResponseListCollectionResults](docs/BaseResponseListCollectionResults.md)
 - [BaseResponseListCommentResponse](docs/BaseResponseListCommentResponse.md)
 - [BaseResponseListDieMatch](docs/BaseResponseListDieMatch.md)
 - [BaseResponseListFunctionBoxPlotConfidence](docs/BaseResponseListFunctionBoxPlotConfidence.md)
 - [BaseResponseListFunctionNameHistory](docs/BaseResponseListFunctionNameHistory.md)
 - [BaseResponseListSBOM](docs/BaseResponseListSBOM.md)
 - [BaseResponseListSimilarFunctionsResponse](docs/BaseResponseListSimilarFunctionsResponse.md)
 - [BaseResponseListTagOriginBoxPlotConfidence](docs/BaseResponseListTagOriginBoxPlotConfidence.md)
 - [BaseResponseListUserActivityResponse](docs/BaseResponseListUserActivityResponse.md)
 - [BaseResponseLoginResponse](docs/BaseResponseLoginResponse.md)
 - [BaseResponseLogs](docs/BaseResponseLogs.md)
 - [BaseResponseModelsResponse](docs/BaseResponseModelsResponse.md)
 - [BaseResponseNearestNeighborAnalysis](docs/BaseResponseNearestNeighborAnalysis.md)
 - [BaseResponseNetworkOverviewResponse](docs/BaseResponseNetworkOverviewResponse.md)
 - [BaseResponseParams](docs/BaseResponseParams.md)
 - [BaseResponseProcessDumps](docs/BaseResponseProcessDumps.md)
 - [BaseResponseProcessRegistry](docs/BaseResponseProcessRegistry.md)
 - [BaseResponseProcessTree](docs/BaseResponseProcessTree.md)
 - [BaseResponseQueuedSecurityChecksTaskResponse](docs/BaseResponseQueuedSecurityChecksTaskResponse.md)
 - [BaseResponseRecent](docs/BaseResponseRecent.md)
 - [BaseResponseSecurityChecksResponse](docs/BaseResponseSecurityChecksResponse.md)
 - [BaseResponseStatus](docs/BaseResponseStatus.md)
 - [BaseResponseStr](docs/BaseResponseStr.md)
 - [BaseResponseSymbolsInfo](docs/BaseResponseSymbolsInfo.md)
 - [BaseResponseTTPS](docs/BaseResponseTTPS.md)
 - [BaseResponseTagSearchResponse](docs/BaseResponseTagSearchResponse.md)
 - [BaseResponseTaskResponse](docs/BaseResponseTaskResponse.md)
 - [BaseResponseVulnerabilities](docs/BaseResponseVulnerabilities.md)
 - [Basic](docs/Basic.md)
 - [BinaryAdditionalDetailsDataResponse](docs/BinaryAdditionalDetailsDataResponse.md)
 - [BinaryAdditionalResponse](docs/BinaryAdditionalResponse.md)
 - [BinaryAnnForm](docs/BinaryAnnForm.md)
 - [BinaryAnnListResponse](docs/BinaryAnnListResponse.md)
 - [BinaryConfig](docs/BinaryConfig.md)
 - [BinaryDetailsResponse](docs/BinaryDetailsResponse.md)
 - [BinaryExternalsResponse](docs/BinaryExternalsResponse.md)
 - [BinarySearchResponse](docs/BinarySearchResponse.md)
 - [BinarySearchResult](docs/BinarySearchResult.md)
 - [BinaryTaskStatus](docs/BinaryTaskStatus.md)
 - [Block](docs/Block.md)
 - [BlockCommentsGenerationForFunctionResponse](docs/BlockCommentsGenerationForFunctionResponse.md)
 - [Boundary](docs/Boundary.md)
 - [BoxPlotConfidence](docs/BoxPlotConfidence.md)
 - [CalleeFunctionInfo](docs/CalleeFunctionInfo.md)
 - [CalleesCallerFunctionsResponse](docs/CalleesCallerFunctionsResponse.md)
 - [CallerFunctionInfo](docs/CallerFunctionInfo.md)
 - [Capabilities](docs/Capabilities.md)
 - [Capability](docs/Capability.md)
 - [CheckSecurityChecksTaskResponse](docs/CheckSecurityChecksTaskResponse.md)
 - [ChildBinariesResponse](docs/ChildBinariesResponse.md)
 - [CodeSignatureModel](docs/CodeSignatureModel.md)
 - [CollectionBinariesUpdateRequest](docs/CollectionBinariesUpdateRequest.md)
 - [CollectionBinariesUpdateResponse](docs/CollectionBinariesUpdateResponse.md)
 - [CollectionBinaryResponse](docs/CollectionBinaryResponse.md)
 - [CollectionCreateRequest](docs/CollectionCreateRequest.md)
 - [CollectionListItem](docs/CollectionListItem.md)
 - [CollectionResponse](docs/CollectionResponse.md)
 - [CollectionResponseBinariesInner](docs/CollectionResponseBinariesInner.md)
 - [CollectionScope](docs/CollectionScope.md)
 - [CollectionSearchResponse](docs/CollectionSearchResponse.md)
 - [CollectionSearchResult](docs/CollectionSearchResult.md)
 - [CollectionTagsUpdateRequest](docs/CollectionTagsUpdateRequest.md)
 - [CollectionTagsUpdateResponse](docs/CollectionTagsUpdateResponse.md)
 - [CollectionUpdateRequest](docs/CollectionUpdateRequest.md)
 - [CommentBase](docs/CommentBase.md)
 - [CommentResponse](docs/CommentResponse.md)
 - [CommentUpdateRequest](docs/CommentUpdateRequest.md)
 - [Communities](docs/Communities.md)
 - [CommunityMatchPercentages](docs/CommunityMatchPercentages.md)
 - [ConfidenceType](docs/ConfidenceType.md)
 - [Context](docs/Context.md)
 - [Created](docs/Created.md)
 - [DecompilationCommentContext](docs/DecompilationCommentContext.md)
 - [DecompilationResponse](docs/DecompilationResponse.md)
 - [DieMatch](docs/DieMatch.md)
 - [DynamicExecutionStatusInput](docs/DynamicExecutionStatusInput.md)
 - [ELFImportModel](docs/ELFImportModel.md)
 - [ELFModel](docs/ELFModel.md)
 - [ELFRelocation](docs/ELFRelocation.md)
 - [ELFSection](docs/ELFSection.md)
 - [ELFSecurity](docs/ELFSecurity.md)
 - [ELFSegment](docs/ELFSegment.md)
 - [ELFSymbol](docs/ELFSymbol.md)
 - [ElfDynamicEntry](docs/ElfDynamicEntry.md)
 - [EntrypointModel](docs/EntrypointModel.md)
 - [Enumeration](docs/Enumeration.md)
 - [ErrorModel](docs/ErrorModel.md)
 - [ExportModel](docs/ExportModel.md)
 - [ExportedBinaryAnnResult](docs/ExportedBinaryAnnResult.md)
 - [ExternalResponse](docs/ExternalResponse.md)
 - [FileFormat](docs/FileFormat.md)
 - [FileHashes](docs/FileHashes.md)
 - [FileMetadata](docs/FileMetadata.md)
 - [Filters](docs/Filters.md)
 - [FunctionAnalysisThreatScoreData](docs/FunctionAnalysisThreatScoreData.md)
 - [FunctionBlockDestinationResponse](docs/FunctionBlockDestinationResponse.md)
 - [FunctionBlockResponse](docs/FunctionBlockResponse.md)
 - [FunctionBlocksResponse](docs/FunctionBlocksResponse.md)
 - [FunctionBoundary](docs/FunctionBoundary.md)
 - [FunctionBoxPlotConfidence](docs/FunctionBoxPlotConfidence.md)
 - [FunctionCapabilityResponse](docs/FunctionCapabilityResponse.md)
 - [FunctionCommentCreateRequest](docs/FunctionCommentCreateRequest.md)
 - [FunctionDataTypes](docs/FunctionDataTypes.md)
 - [FunctionDataTypesList](docs/FunctionDataTypesList.md)
 - [FunctionDataTypesListItem](docs/FunctionDataTypesListItem.md)
 - [FunctionDataTypesParams](docs/FunctionDataTypesParams.md)
 - [FunctionDataTypesStatus](docs/FunctionDataTypesStatus.md)
 - [FunctionHeader](docs/FunctionHeader.md)
 - [FunctionInfoInput](docs/FunctionInfoInput.md)
 - [FunctionInfoInputFuncDepsInner](docs/FunctionInfoInputFuncDepsInner.md)
 - [FunctionInfoOutput](docs/FunctionInfoOutput.md)
 - [FunctionLocalVariableResponse](docs/FunctionLocalVariableResponse.md)
 - [FunctionMappingFull](docs/FunctionMappingFull.md)
 - [FunctionNameConfidenceBody](docs/FunctionNameConfidenceBody.md)
 - [FunctionNameHistory](docs/FunctionNameHistory.md)
 - [FunctionNameInput](docs/FunctionNameInput.md)
 - [FunctionParamResponse](docs/FunctionParamResponse.md)
 - [FunctionRename](docs/FunctionRename.md)
 - [FunctionRenameMap](docs/FunctionRenameMap.md)
 - [FunctionSearchResponse](docs/FunctionSearchResponse.md)
 - [FunctionSearchResult](docs/FunctionSearchResult.md)
 - [FunctionString](docs/FunctionString.md)
 - [FunctionStringsResponse](docs/FunctionStringsResponse.md)
 - [FunctionTaskResponse](docs/FunctionTaskResponse.md)
 - [FunctionTaskStatus](docs/FunctionTaskStatus.md)
 - [FunctionThreatScore](docs/FunctionThreatScore.md)
 - [FunctionTypeInput](docs/FunctionTypeInput.md)
 - [FunctionTypeOutput](docs/FunctionTypeOutput.md)
 - [FunctionsDetailResponse](docs/FunctionsDetailResponse.md)
 - [FunctionsListRename](docs/FunctionsListRename.md)
 - [GenerateFunctionDataTypes](docs/GenerateFunctionDataTypes.md)
 - [GenerationStatusList](docs/GenerationStatusList.md)
 - [GetAiDecompilationRatingResponse](docs/GetAiDecompilationRatingResponse.md)
 - [GetAiDecompilationTask](docs/GetAiDecompilationTask.md)
 - [GetPublicUserResponse](docs/GetPublicUserResponse.md)
 - [GetUserResponse](docs/GetUserResponse.md)
 - [GlobalVariable](docs/GlobalVariable.md)
 - [ISA](docs/ISA.md)
 - [IconModel](docs/IconModel.md)
 - [ImportModel](docs/ImportModel.md)
 - [InverseFunctionMapItem](docs/InverseFunctionMapItem.md)
 - [InverseStringMapItem](docs/InverseStringMapItem.md)
 - [InverseValue](docs/InverseValue.md)
 - [ListCollectionResults](docs/ListCollectionResults.md)
 - [LoginRequest](docs/LoginRequest.md)
 - [LoginResponse](docs/LoginResponse.md)
 - [Logs](docs/Logs.md)
 - [MetaModel](docs/MetaModel.md)
 - [ModelName](docs/ModelName.md)
 - [ModelsResponse](docs/ModelsResponse.md)
 - [NearestNeighbor](docs/NearestNeighbor.md)
 - [NetworkOverviewDns](docs/NetworkOverviewDns.md)
 - [NetworkOverviewDnsAnswer](docs/NetworkOverviewDnsAnswer.md)
 - [NetworkOverviewMetadata](docs/NetworkOverviewMetadata.md)
 - [NetworkOverviewResponse](docs/NetworkOverviewResponse.md)
 - [Order](docs/Order.md)
 - [Origin](docs/Origin.md)
 - [PDBDebugModel](docs/PDBDebugModel.md)
 - [PEModel](docs/PEModel.md)
 - [PaginationModel](docs/PaginationModel.md)
 - [Params](docs/Params.md)
 - [Platform](docs/Platform.md)
 - [Process](docs/Process.md)
 - [ProcessDump](docs/ProcessDump.md)
 - [ProcessDumpMetadata](docs/ProcessDumpMetadata.md)
 - [ProcessDumps](docs/ProcessDumps.md)
 - [ProcessDumpsData](docs/ProcessDumpsData.md)
 - [ProcessRegistry](docs/ProcessRegistry.md)
 - [ProcessTree](docs/ProcessTree.md)
 - [QueuedSecurityChecksTaskResponse](docs/QueuedSecurityChecksTaskResponse.md)
 - [ReAnalysisForm](docs/ReAnalysisForm.md)
 - [Recent](docs/Recent.md)
 - [Registry](docs/Registry.md)
 - [RelativeBinaryResponse](docs/RelativeBinaryResponse.md)
 - [SBOM](docs/SBOM.md)
 - [SBOMPackage](docs/SBOMPackage.md)
 - [SandboxOptions](docs/SandboxOptions.md)
 - [ScrapeThirdPartyConfig](docs/ScrapeThirdPartyConfig.md)
 - [SearchBinaryIds](docs/SearchBinaryIds.md)
 - [SearchFunctionIds](docs/SearchFunctionIds.md)
 - [SectionModel](docs/SectionModel.md)
 - [SecurityChecksResponse](docs/SecurityChecksResponse.md)
 - [SecurityChecksResult](docs/SecurityChecksResult.md)
 - [SecurityModel](docs/SecurityModel.md)
 - [SeverityType](docs/SeverityType.md)
 - [SimilarFunctionsResponse](docs/SimilarFunctionsResponse.md)
 - [SingleCodeCertificateModel](docs/SingleCodeCertificateModel.md)
 - [SingleCodeSignatureModel](docs/SingleCodeSignatureModel.md)
 - [SinglePDBEntryModel](docs/SinglePDBEntryModel.md)
 - [SingleSectionModel](docs/SingleSectionModel.md)
 - [StackVariable](docs/StackVariable.md)
 - [StatusInput](docs/StatusInput.md)
 - [StatusOutput](docs/StatusOutput.md)
 - [StringFunctions](docs/StringFunctions.md)
 - [Structure](docs/Structure.md)
 - [StructureMember](docs/StructureMember.md)
 - [Symbols](docs/Symbols.md)
 - [SymbolsInfo](docs/SymbolsInfo.md)
 - [TTPS](docs/TTPS.md)
 - [TTPSAttack](docs/TTPSAttack.md)
 - [TTPSData](docs/TTPSData.md)
 - [TTPSElement](docs/TTPSElement.md)
 - [TTPSOccurance](docs/TTPSOccurance.md)
 - [TagConfidenceBody](docs/TagConfidenceBody.md)
 - [TagInput](docs/TagInput.md)
 - [TagOriginBoxPlotConfidence](docs/TagOriginBoxPlotConfidence.md)
 - [TagOutput](docs/TagOutput.md)
 - [TagResponse](docs/TagResponse.md)
 - [TagSearchResponse](docs/TagSearchResponse.md)
 - [TagSearchResult](docs/TagSearchResult.md)
 - [Tags](docs/Tags.md)
 - [TaskResponse](docs/TaskResponse.md)
 - [TaskStatus](docs/TaskStatus.md)
 - [ThreatScoreFunctionBody](docs/ThreatScoreFunctionBody.md)
 - [TimestampModel](docs/TimestampModel.md)
 - [TypeDefinition](docs/TypeDefinition.md)
 - [UpdateFunctionDataTypes](docs/UpdateFunctionDataTypes.md)
 - [UpsertAiDecomplationRatingRequest](docs/UpsertAiDecomplationRatingRequest.md)
 - [UserActivityResponse](docs/UserActivityResponse.md)
 - [Vulnerabilities](docs/Vulnerabilities.md)
 - [Vulnerability](docs/Vulnerability.md)
 - [VulnerabilityType](docs/VulnerabilityType.md)
 - [Workspace](docs/Workspace.md)
