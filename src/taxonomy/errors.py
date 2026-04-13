class AgenticTestingError(Exception):
    """Base error for Domain 1 (Taxonomy) in Agentic Testing."""

    pass


class InfrastructureError(AgenticTestingError):
    """Raised when external commands or processes fail."""

    pass


class AnalysisError(AgenticTestingError):
    """Raised when parsing or static analysis fails."""

    pass


class GenerationError(AgenticTestingError):
    """Raised when data generation bounds are exceeded."""

    pass
