import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import tempfile
import pytest
from clyp.std import fs, json, math, random, time
import time as pytime

# --- fs.py tests ---

def test_fs_write_and_read_file():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
    try:
        fs.write_file(tmp_path, "hello world")
        content = fs.read_file(tmp_path)
        assert content == "hello world"
    finally:
        os.remove(tmp_path)

def test_fs_file_exists(tmp_path='.'):
    filename = os.path.join(tmp_path, "test_exists.txt")
    with open(filename, "w") as f:
        f.write("data")
    assert fs.file_exists(filename)
    os.remove(filename)
    assert not fs.file_exists(filename)

def test_fs_list_dir():
    with tempfile.TemporaryDirectory() as d:
        filenames = ["a.txt", "b.txt"]
        for name in filenames:
            open(os.path.join(d, name), "w").close()
        files = fs.list_dir(d)
        assert set(files) >= set(filenames)

def test_fs_remove_file():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
    fs.write_file(tmp_path, "data")
    assert fs.file_exists(tmp_path)
    fs.remove_file(tmp_path)
    assert not fs.file_exists(tmp_path)

def test_fs_make_and_remove_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        new_dir = os.path.join(tmpdir, "subdir")
        fs.make_dir(new_dir)
        assert os.path.isdir(new_dir)
        fs.remove_dir(new_dir)
        assert not os.path.exists(new_dir)

def test_fs_read_file_not_exists():
    with pytest.raises(Exception):
        fs.read_file("nonexistent_file.txt")

# --- json.py tests ---

def test_json_load_and_dump():
    data = {"a": 1, "b": [2, 3]}
    s = json.dumps(data)
    assert isinstance(s, str)
    loaded = json.loads(s)
    assert loaded == data

def test_json_invalid_load():
    with pytest.raises(Exception):
        json.loads("{invalid json}")

def test_json_dump_and_load_list():
    data = [1, 2, 3, {"x": "y"}]
    s = json.dumps(data)
    loaded = json.loads(s)
    assert loaded == data

# --- math.py tests ---

def test_math_basic_operations():
    assert math.add(2, 3) == 5
    assert math.sub(5, 2) == 3
    assert math.mul(2, 4) == 8
    assert math.div(8, 2) == 4

def test_math_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        math.div(1, 0)

def test_math_advanced():
    assert math.sqrt(9) == 3
    assert math.pow(2, 3) == 8

def test_math_negative_sqrt():
    with pytest.raises(ValueError):
        math.sqrt(-1)

def test_math_float_operations():
    assert math.add(2.5, 3.5) == 6.0
    assert math.div(7.5, 2.5) == 3.0

# --- random.py tests ---

def test_random_randint():
    for _ in range(10):
        val = random.randint(1, 10)
        assert 1 <= val <= 10

def test_random_choice():
    seq = [1, 2, 3]
    for _ in range(10):
        assert random.choice(seq) in seq

def test_random_shuffle():
    seq = [1, 2, 3, 4]
    orig = seq[:]
    random.shuffle(seq)
    assert sorted(seq) == sorted(orig)

def test_random_randfloat():
    for _ in range(10):
        val = random.randfloat(0.0, 1.0)
        assert 0.0 <= val <= 1.0

def test_random_sample():
    seq = [1, 2, 3, 4, 5]
    sample = random.sample(seq, 3)
    assert len(sample) == 3
    for item in sample:
        assert item in seq

# --- time.py tests ---

def test_time_sleep(monkeypatch):
    called = []
    def fake_sleep(seconds):
        called.append(seconds)
    monkeypatch.setattr(time, "sleep", fake_sleep)
    time.sleep(2)
    assert called == [2]

def test_time_now():
    t1 = time.now()
    t2 = pytime.time()
    # If time.now() returns a DateTime object, get its timestamp
    if hasattr(t1, "timestamp"):
        t1_ts = t1.timestamp()
    else:
        t1_ts = t1
    assert abs(t1_ts - t2) < 2  # within 2 seconds

def test_time_format():
    ts = 1609459200  # 2021-01-01 00:00:00 UTC
    formatted = time.format(ts)
    assert "2021" in formatted
    assert "00:00:00" in formatted

def test_time_format_invalid():
    with pytest.raises(Exception):
        time.format("not_a_timestamp")