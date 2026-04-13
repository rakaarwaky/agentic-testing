from src.agent.container import get_container, Container


def test_get_container_singleton():
    c1 = get_container()
    c2 = get_container()
    assert isinstance(c1, Container)
    assert c1 is c2
