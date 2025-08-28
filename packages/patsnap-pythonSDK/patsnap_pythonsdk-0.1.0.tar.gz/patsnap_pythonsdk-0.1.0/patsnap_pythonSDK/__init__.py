from .client import PatsnapClient
from .auth import AuthClient
from .errors import AuthError, ApiError
from .models import (
    PatentSearchPnRequest, 
    PatentBaseV2Response, 
    SearchPatentV2Response,
    CompanySearchRequest,
    CurrentAssigneeSearchRequest,
    DefensePatentSearchRequest,
    SimilarPatentSearchRequest,
    SemanticResult,
    SearchComputeV2Response,
    SemanticSearchRequest,
    FileUrlResponse,
    ImageSearchSingleRequest,
    PatentMessage,
    ImageSearchResponse,
    ImageSearchMultipleRequest,
    AnalyticsQuerySearchCountRequest,
    SearchPatentCountResponse,
    SortField,
    AnalyticsQuerySearchRequest,
)

# Global instance placeholder - will be initialized when configure() is called
patsnap = None

def configure(client_id: str, client_secret: str, **kwargs):
    """Configure the global patsnap instance.
    
    Args:
        client_id: Your Patsnap client ID
        client_secret: Your Patsnap client secret
        **kwargs: Additional arguments passed to PatsnapClient
    
    Returns:
        The configured PatsnapClient instance
    
    Example:
        >>> import patsnap_pythonSDK as patsnap
        >>> patsnap.configure(client_id="your_id", client_secret="your_secret")
        >>> results = patsnap.analytics.search.query_count(query_text="AI")
    """
    global patsnap
    patsnap = PatsnapClient(client_id=client_id, client_secret=client_secret, **kwargs)
    return patsnap

def __getattr__(name):
    """Delegate attribute access to the global patsnap instance.
    
    This allows users to access patsnap.analytics.search.query_count() 
    instead of patsnap.patsnap.analytics.search.query_count()
    """
    if patsnap is None:
        raise AttributeError(
            f"'{name}' is not available. You must call patsnap.configure() first.\n"
            f"Example:\n"
            f"  import patsnap_pythonSDK as patsnap\n"
            f"  patsnap.configure(client_id='your_id', client_secret='your_secret')\n"
            f"  patsnap.{name}  # Now this will work"
        )
    
    if hasattr(patsnap, name):
        return getattr(patsnap, name)
    
    raise AttributeError(f"module 'patsnap_pythonSDK' has no attribute '{name}'")

__all__ = [
    "PatsnapClient", 
    "AuthClient", 
    "AuthError", 
    "ApiError",
    "PatentSearchPnRequest",
    "PatentBaseV2Response", 
    "SearchPatentV2Response",
    "CompanySearchRequest",
    "CurrentAssigneeSearchRequest",
    "DefensePatentSearchRequest",
    "SimilarPatentSearchRequest",
    "SemanticResult",
    "SearchComputeV2Response",
    "SemanticSearchRequest",
    "FileUrlResponse",
    "ImageSearchSingleRequest",
    "PatentMessage",
    "ImageSearchResponse",
    "ImageSearchMultipleRequest",
        "AnalyticsQuerySearchCountRequest",
    "SearchPatentCountResponse", 
    "SortField",
    "AnalyticsQuerySearchRequest",
    "AnalyticsQueryFilterRequest",
    "SearchPatentFieldResponse",
    "PatentDataFieldResponse",
    "configure",
    "patsnap",
]


