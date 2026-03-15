from src.core.capabilities.synthetic_data.actions import SimpleDataGenerator


def test_generate_strings():
    gen = SimpleDataGenerator()
    res = gen.generate_strings(count=3)
    assert len(res) == 9  # 6 defaults + 3
    assert None in res
    assert "" in res


def test_generate_numbers():
    gen = SimpleDataGenerator()
    res = gen.generate_numbers(count=2)
    assert len(res) == 11  # 9 defaults + 2
    assert 0 in res


def test_generate_json():
    gen = SimpleDataGenerator()
    res = gen.generate_json(count=1)
    assert len(res) == 6  # 5 defaults + 1
    assert res[0] == {}


def test_generate_all():
    gen = SimpleDataGenerator()
    res = gen.generate_all()
    assert "strings" in res
    assert "emails" in res
