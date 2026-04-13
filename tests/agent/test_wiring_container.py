"""Tests for agent/dependency_wiring_container.py — dependency wiring."""

from src.agent.dependency_wiring_container import (
    wire_dependencies,
    LAYER_RULES,
    LAYER_MAP,
)


class TestLayerRules:
    """Verify architecture layer constraint definitions."""

    def test_layer_rules_is_list(self):
        assert isinstance(LAYER_RULES, list)

    def test_layer_rules_not_empty(self):
        assert len(LAYER_RULES) > 0

    def test_each_rule_is_tuple_of_three(self):
        for rule in LAYER_RULES:
            assert isinstance(rule, tuple)
            assert len(rule) == 3

    def test_capabilities_cannot_import_surfaces(self):
        """First rule: capabilities must not import surfaces."""
        rule = LAYER_RULES[0]
        assert rule[0] == "capabilities"
        assert rule[1] == "surfaces"

    def test_infrastructure_cannot_import_surfaces(self):
        """Second rule: infrastructure must not import surfaces."""
        rule = LAYER_RULES[1]
        assert rule[0] == "infrastructure"
        assert rule[1] == "surfaces"


class TestLayerMap:
    """Verify layer mapping definitions."""

    def test_layer_map_has_all_layers(self):
        expected = {"infrastructure", "capabilities", "surfaces", "agent", "taxonomy"}
        assert set(LAYER_MAP.keys()) == expected

    def test_layer_map_identity(self):
        """Each layer maps to itself."""
        for key, value in LAYER_MAP.items():
            assert key == value


class TestWireDependencies:
    """Verify wire_dependencies() returns all expected components."""

    def test_returns_dict(self):
        result = wire_dependencies()
        assert isinstance(result, dict)

    def test_has_all_expected_keys(self):
        result = wire_dependencies()
        expected_keys = {
            "runner",
            "file_system",
            "healer",
            "test_use_case",
            "analyzer",
            "auditor",
            "generator",
            "test_generator",
            "governance",
        }
        assert set(result.keys()) == expected_keys

    def test_runner_is_pytest_runner(self):
        from src.infrastructure.shell_adapter import PytestRunner

        result = wire_dependencies()
        assert isinstance(result["runner"], PytestRunner)

    def test_file_system_is_local(self):
        from src.infrastructure.file_system_provider import LocalFileSystem

        result = wire_dependencies()
        assert isinstance(result["file_system"], LocalFileSystem)

    def test_healer_is_heuristic(self):
        from src.capabilities.autonomous_testing_healing_adapter import (
            HeuristicHealer,
        )

        result = wire_dependencies()
        assert isinstance(result["healer"], HeuristicHealer)

    def test_test_use_case_has_runner_and_healer(self):
        result = wire_dependencies()
        use_case = result["test_use_case"]
        assert hasattr(use_case, "runner")
        assert hasattr(use_case, "healer")

    def test_analyzer_is_ast_analyzer(self):
        from src.capabilities.code_analysis_actions import AstAnalyzer

        result = wire_dependencies()
        assert isinstance(result["analyzer"], AstAnalyzer)

    def test_auditor_is_coverage_auditor(self):
        from src.capabilities.code_analysis_audit_analyzer import CoverageAuditor

        result = wire_dependencies()
        assert isinstance(result["auditor"], CoverageAuditor)

    def test_generator_is_simple_data_generator(self):
        from src.capabilities.synthetic_data_actions import SimpleDataGenerator

        result = wire_dependencies()
        assert isinstance(result["generator"], SimpleDataGenerator)

    def test_governance_is_governance_adapter(self):
        from src.capabilities.governance_adapter import GovernanceAdapter

        result = wire_dependencies()
        assert isinstance(result["governance"], GovernanceAdapter)

    def test_no_none_values(self):
        result = wire_dependencies()
        for key, value in result.items():
            assert value is not None, f"Component '{key}' is None"

    def test_multiple_calls_independent(self):
        """Each call should produce independent instances."""
        r1 = wire_dependencies()
        r2 = wire_dependencies()
        for key in r1:
            assert r1[key] is not r2[key], f"Component '{key}' is shared"
