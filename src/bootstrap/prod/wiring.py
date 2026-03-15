from ...infrastructure.shell_adapter import PytestRunner
from ...infrastructure.file_system import LocalFileSystem
from ...core.capabilities.autonomous_testing.actions import RunTestWithHealingUseCase
from ...core.capabilities.autonomous_testing.healer import HeuristicHealer
from ...core.capabilities.code_analysis.actions import AstAnalyzer
from ...core.capabilities.code_analysis.auditor import CoverageAuditor
from ...core.capabilities.synthetic_data.actions import SimpleDataGenerator
from ...core.capabilities.autogenerate.actions import AutogenerateTestUseCase


def wire_dependencies():
    """Level 3b: Production - Wiring specific infrastructure and capabilities."""

    # Infrastructure
    runner = PytestRunner()
    file_system = LocalFileSystem()

    # Capability: Autonomous Testing
    healer = HeuristicHealer(file_system)
    test_use_case = RunTestWithHealingUseCase(runner, healer)

    # Capability: Code Analysis
    analyzer = AstAnalyzer()
    auditor = CoverageAuditor()

    # Capability: Synthetic Data
    generator = SimpleDataGenerator()

    # Capability: Autogenerate
    test_generator = AutogenerateTestUseCase(analyzer, file_system)

    return {
        "runner": runner,
        "healer": healer,
        "test_use_case": test_use_case,
        "analyzer": analyzer,
        "auditor": auditor,
        "generator": generator,
        "test_generator": test_generator,
    }
