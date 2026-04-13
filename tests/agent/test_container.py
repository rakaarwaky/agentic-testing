"""Tests for the DI container."""
import pytest
from src.agent.container import Container, get_container, reset_container


def test_container_init():
    """Test container initialization."""
    reset_container()
    container = Container()
    assert container.runner is not None
    assert container.file_system is not None
    assert container.healer is not None
    assert container.test_use_case is not None
    assert container.analyzer is not None
    assert container.auditor is not None
    assert container.generator is not None
    assert container.test_generator is not None
    reset_container()


def test_get_container_singleton():
    """Test that get_container returns the same instance."""
    reset_container()
    c1 = get_container()
    c2 = get_container()
    assert c1 is c2
    reset_container()


def test_reset_container():
    """Test that reset_container clears the singleton."""
    reset_container()
    c1 = get_container()
    reset_container()
    c2 = get_container()
    assert c1 is not c2
    reset_container()
