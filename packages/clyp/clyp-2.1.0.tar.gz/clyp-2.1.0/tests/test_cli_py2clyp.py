import os
import sys
import clyp.cli as cli_mod


def _run_cli(args, cwd, monkeypatch, capsys):
    monkeypatch.chdir(cwd)
    monkeypatch.setenv("PYTHONPATH", os.getcwd())
    monkeypatch.setattr(sys, "argv", ["clyp"] + args)
    try:
        cli_mod.main()
    except SystemExit as e:
        if e.code not in (0, None):
            raise
    return capsys.readouterr()


def test_py2clyp_basic(tmp_path, monkeypatch, capsys):
    py_file = tmp_path / "hello.py"
    py_file.write_text('def greet(name):\n    print(f"Hello, {name}!")\n')
    result = _run_cli(
        ["py2clyp", str(py_file), "--print"], tmp_path, monkeypatch, capsys
    )
    assert "function greet" in result.out or "def greet" in result.out
    assert "print" in result.out


def test_py2clyp_format(tmp_path, monkeypatch, capsys):
    py_file = tmp_path / "add.py"
    py_file.write_text("def add(a, b):\n return a+b\n")
    result = _run_cli(
        ["py2clyp", str(py_file), "--format", "--print"], tmp_path, monkeypatch, capsys
    )
    # The improved formatter should successfully format the transpiled code
    assert "function add" in result.out
    # Check that formatting was applied (spacing improvements)
    assert "return a + b" in result.out  # Formatted with proper spacing


def test_py2clyp_check_success(tmp_path, monkeypatch, capsys):
    py_file = tmp_path / "ok.py"
    py_file.write_text("def foo():\n    pass\n")
    result = _run_cli(
        ["py2clyp", str(py_file), "--check"], tmp_path, monkeypatch, capsys
    )
    assert "can be transpiled" in result.out


def test_py2clyp_diff(tmp_path, monkeypatch, capsys):
    py_file = tmp_path / "diff.py"
    py_file.write_text("def foo():\n    return 1\n")
    result = _run_cli(
        ["py2clyp", str(py_file), "--diff"], tmp_path, monkeypatch, capsys
    )
    assert "---" in result.out and "+++" in result.out


def test_py2clyp_output_file(tmp_path, monkeypatch, capsys):
    py_file = tmp_path / "out.py"
    py_file.write_text("def foo():\n    return 42\n")
    out_file = tmp_path / "out.clyp"
    _run_cli(
        ["py2clyp", str(py_file), "-o", str(out_file)], tmp_path, monkeypatch, capsys
    )
    assert out_file.exists()
    content = out_file.read_text()
    assert "function foo" in content or "def foo" in content


def test_py2clyp_overwrite(tmp_path, monkeypatch, capsys):
    py_file = tmp_path / "overwrite.py"
    py_file.write_text("def foo():\n    return 99\n")
    _run_cli(["py2clyp", str(py_file), "--overwrite"], tmp_path, monkeypatch, capsys)
    content = py_file.read_text()
    assert "function foo" in content or "def foo" in content
