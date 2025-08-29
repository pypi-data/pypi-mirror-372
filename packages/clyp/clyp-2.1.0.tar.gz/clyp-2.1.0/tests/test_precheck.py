import pytest
from clyp.precheck import precheck_clyp_code

@pytest.mark.parametrize(
    "code,expected",
    [
        (
            "def foo(x) returns int { }",
            "ERROR [ A101 ]"
        ),
        (
            "repeat [5] times",
            "WARNING [ W501 ]"
        ),
        (
            "x: int = 'hello'",
            "ERROR [ C100 ]"
        ),
        (
            "y: float = 42",
            "ERROR [ C100 ]"
        ),
        (
            "z: str = 123",
            "ERROR [ C100 ]"
        ),
        (
            "b: bool = 1",
            "ERROR [ C100 ]"
        ),
        (
            "lst: list = 123",
            "ERROR [ C101 ]"
        ),
        (
            "d: dict = 123",
            "ERROR [ C102 ]"
        ),
        (
            "def bar(self) { }",
            "ERROR [ L100 ]"
        ),
    ]
)
def test_precheck_errors(code, expected):
    errors = precheck_clyp_code(code)
    assert any(expected in err for err in errors)

def test_version_major_warning():
    code = (
        "define clyp_version 99.0.0\n"
        "define version_strictness major\n"
    )
    errors = precheck_clyp_code(code)
    assert any("WARNING [ U500 ]" in err for err in errors)

def test_version_minor_warning():
    code = (
        "define clyp_version 0.99.0\n"
        "define version_strictness minor\n"
    )
    errors = precheck_clyp_code(code)
    assert any("WARNING [ U501 ]" in err for err in errors)

def test_version_patch_warning():
    code = (
        "define clyp_version 0.0.99\n"
        "define version_strictness patch\n"
    )
    errors = precheck_clyp_code(code)
    assert any("WARNING [ U502 ]" in err for err in errors)

def test_no_errors():
    code = (
        "define clyp_version 0.0.1\n"
        "define version_strictness major\n"
        "x: int = 42\n"
        "y: float = 3.14\n"
        "z: str = \"hello\"\n"
        "b: bool = true\n"
        "lst: list = [1,2,3]\n"
        "d: dict = {\"a\": 1}\n"
    )
    errors = precheck_clyp_code(code)
    assert errors == []

