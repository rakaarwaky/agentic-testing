from ..infrastructure.shell_adapter import PytestRunner
from ..infrastructure.file_system import LocalFileSystem
from ..capabilities.autonomous_testing_actions import RunTestWithHealingUseCase
from ..capabilities.autonomous_testing_healer import HeuristicHealer
from ..capabilities.code_analysis_actions import AstAnalyzer
from ..capabilities.code_analysis_auditor import CoverageAuditor
from ..capabilities.synthetic_data_actions import SimpleDataGenerator
from ..capabilities.autogenerate_actions import AutogenerateTestUseCase


import typing

def wire_dependencies() -> dict[str, typing.Any]:
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
        "file_system": file_system,
        "healer": healer,
        "test_use_case": test_use_case,
        "analyzer": analyzer,
        "auditor": auditor,
        "generator": generator,
        "test_generator": test_generator,
    }
