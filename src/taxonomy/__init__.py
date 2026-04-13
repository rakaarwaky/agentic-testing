"""taxonomy — Shared language for all domains (VOs, entities, interfaces, errors, events)."""

__all__ = [
    # Value Objects: Core
    "Severity", "ErrorCode", "Position", "Score",
    # Value Objects: Identifiers
    "TestName", "FilePath", "SymbolName", "DirectoryPath",
    # Value Objects: Domain
    "ScopeRef", "Location",
    # Entities
    "TestResult", "FailureMetadata",
    # Interfaces
    "ITestRunner", "ITestHealer", "ICodeAnalyzer",
    "IQualityAuditor", "ITestGenerator", "IFileSystem",
    # Errors
    "AgenticTestingError", "InfrastructureError", "AnalysisError", "GenerationError",
    # Events
    "TestRunStarted", "TestRunCompleted", "TestRunFailed", "HealApplied",
]

# -- Value Objects: Core --
from .lint_value_vo import (
    Severity as Severity,
    ErrorCode as ErrorCode,
    Position as Position,
    Score as Score,
)

# -- Value Objects: Identifiers --
from .lint_identifier_vo import (
    TestName as TestName,
    FilePath as FilePath,
    SymbolName as SymbolName,
    DirectoryPath as DirectoryPath,
)

# -- Value Objects: Domain --
from .lint_domain_vo import (
    ScopeRef as ScopeRef,
    Location as Location,
)

# -- Entities --
from .test_result_entity import (
    TestResult as TestResult,
    FailureMetadata as FailureMetadata,
)

# -- Interfaces --
from .test_interface_vo import (
    ITestRunner as ITestRunner,
    ITestHealer as ITestHealer,
    ICodeAnalyzer as ICodeAnalyzer,
    IQualityAuditor as IQualityAuditor,
    ITestGenerator as ITestGenerator,
    IFileSystem as IFileSystem,
)

# -- Errors --
from .agentic_error import (
    AgenticTestingError as AgenticTestingError,
    InfrastructureError as InfrastructureError,
    AnalysisError as AnalysisError,
    GenerationError as GenerationError,
)

# -- Events --
from .test_event import (
    TestRunStarted as TestRunStarted,
    TestRunCompleted as TestRunCompleted,
    TestRunFailed as TestRunFailed,
    HealApplied as HealApplied,
)
