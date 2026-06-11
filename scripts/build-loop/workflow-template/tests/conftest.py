import json
import os
import tempfile

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def read_fixture(name):
    path = os.path.join(FIXTURES, name)
    with open(path) as f:
        return f.read()


def read_fixture_json(name):
    return json.loads(read_fixture(name))


def read_root_json(rel_path):
    path = os.path.join(PROJECT_ROOT, rel_path)
    with open(path) as f:
        return json.load(f)


def read_root_file(rel_path):
    path = os.path.join(PROJECT_ROOT, rel_path)
    with open(path) as f:
        return f.read()


def temp_state(data=None):
    if data is None:
        data = read_fixture_json("state.json")
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(data, tmp, indent=2, ensure_ascii=False)
    tmp.flush()
    return tmp.name


def temp_phases():
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(read_fixture_json("phases.json"), tmp, indent=2)
    tmp.flush()
    return tmp.name
