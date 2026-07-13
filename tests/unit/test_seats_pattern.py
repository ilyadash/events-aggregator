from app.utils.seats_pattern import parse_seats_pattern


def test_single_section():
    result = parse_seats_pattern("A1-5")
    assert result == {"A1", "A2", "A3", "A4", "A5"}


def test_multiple_sections():
    result = parse_seats_pattern("A1-3,B1-2")
    assert result == {"A1", "A2", "A3", "B1", "B2"}


def test_three_sections():
    result = parse_seats_pattern("A1-2,B1-3,C1-1")
    assert result == {"A1", "A2", "B1", "B2", "B3", "C1"}


def test_single_seat():
    result = parse_seats_pattern("A1-1")
    assert result == {"A1"}


def test_large_range():
    result = parse_seats_pattern("A1-1000")
    assert len(result) == 1000
    assert "A1" in result
    assert "A1000" in result
    assert "A500" in result


def test_real_pattern():
    result = parse_seats_pattern("A1-1000,B1-2000,C1-3000")
    assert len(result) == 6000
    assert "A1000" in result
    assert "B2000" in result
    assert "C3000" in result


def test_empty_string():
    result = parse_seats_pattern("")
    assert result == set()


def test_whitespace():
    result = parse_seats_pattern(" A1-2 , B1-2 ")
    assert result == {"A1", "A2", "B1", "B2"}
