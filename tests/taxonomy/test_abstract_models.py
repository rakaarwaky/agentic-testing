import pytest
from src.contract import (
    ITestRunner,
    ITestHealer,
    ICodeAnalyzer,
    IQualityAuditor,
)


def test_abstract_methods_raise_not_implemented():
    """Abstract classes cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ITestRunner()

    with pytest.raises(TypeError):
        ITestHealer()

    with pytest.raises(TypeError):
        ICodeAnalyzer()

    with pytest.raises(TypeError):
        IQualityAuditor()
