# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from revengai.api.analyses_comments_api import AnalysesCommentsApi
    from revengai.api.analyses_core_api import AnalysesCoreApi
    from revengai.api.analyses_dynamic_execution_api import AnalysesDynamicExecutionApi
    from revengai.api.analyses_results_metadata_api import AnalysesResultsMetadataApi
    from revengai.api.analyses_security_checks_api import AnalysesSecurityChecksApi
    from revengai.api.authentication_users_api import AuthenticationUsersApi
    from revengai.api.binaries_api import BinariesApi
    from revengai.api.collections_api import CollectionsApi
    from revengai.api.confidence_api import ConfidenceApi
    from revengai.api.external_sources_api import ExternalSourcesApi
    from revengai.api.firmware_api import FirmwareApi
    from revengai.api.functions_ai_decompilation_api import FunctionsAIDecompilationApi
    from revengai.api.functions_block_comments_api import FunctionsBlockCommentsApi
    from revengai.api.functions_core_api import FunctionsCoreApi
    from revengai.api.functions_data_types_api import FunctionsDataTypesApi
    from revengai.api.functions_decompilation_api import FunctionsDecompilationApi
    from revengai.api.functions_renaming_history_api import FunctionsRenamingHistoryApi
    from revengai.api.functions_threat_score_api import FunctionsThreatScoreApi
    from revengai.api.models_api import ModelsApi
    from revengai.api.search_api import SearchApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from revengai.api.analyses_comments_api import AnalysesCommentsApi
from revengai.api.analyses_core_api import AnalysesCoreApi
from revengai.api.analyses_dynamic_execution_api import AnalysesDynamicExecutionApi
from revengai.api.analyses_results_metadata_api import AnalysesResultsMetadataApi
from revengai.api.analyses_security_checks_api import AnalysesSecurityChecksApi
from revengai.api.authentication_users_api import AuthenticationUsersApi
from revengai.api.binaries_api import BinariesApi
from revengai.api.collections_api import CollectionsApi
from revengai.api.confidence_api import ConfidenceApi
from revengai.api.external_sources_api import ExternalSourcesApi
from revengai.api.firmware_api import FirmwareApi
from revengai.api.functions_ai_decompilation_api import FunctionsAIDecompilationApi
from revengai.api.functions_block_comments_api import FunctionsBlockCommentsApi
from revengai.api.functions_core_api import FunctionsCoreApi
from revengai.api.functions_data_types_api import FunctionsDataTypesApi
from revengai.api.functions_decompilation_api import FunctionsDecompilationApi
from revengai.api.functions_renaming_history_api import FunctionsRenamingHistoryApi
from revengai.api.functions_threat_score_api import FunctionsThreatScoreApi
from revengai.api.models_api import ModelsApi
from revengai.api.search_api import SearchApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
