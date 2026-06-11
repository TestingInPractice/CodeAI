import json, os, sys

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")

def validate_required(obj, schema, path=""):
    if "required" in schema:
        for field in schema["required"]:
            if field not in obj:
                return False, f"{path}: missing required field '{field}'"
    return True, None

def validate_type(value, expected_type, path=""):
    type_map = {
        "string": str, "integer": int, "number": (int, float),
        "boolean": bool, "array": list, "object": dict, "null": type(None),
    }
    if isinstance(expected_type, list):
        py_types = tuple(type_map.get(t, type(None)) for t in expected_type)
        if not isinstance(value, py_types):
            valid_names = [t for t in expected_type if t != "null"]
            return False, f"{path}: expected {valid_names}, got {type(value).__name__}"
    else:
        py_type = type_map.get(expected_type, str)
        if not isinstance(value, py_type):
            return False, f"{path}: expected {expected_type}, got {type(value).__name__}"
    return True, None

def validate_enum(value, enum_values, path=""):
    if value not in enum_values:
        return False, f"{path}: '{value}' not in {enum_values}"
    return True, None

def validate_schema(obj, schema, path=""):
    if schema.get("type") == "object":
        ok, err = validate_required(obj, schema, path)
        if not ok: return False, err
        for key, prop_schema in schema.get("properties", {}).items():
            child_path = f"{path}.{key}" if path else key
            if key in obj:
                ok, err = validate_value(obj[key], prop_schema, child_path)
                if not ok: return False, err
    elif schema.get("type") == "array":
        if not isinstance(obj, list):
            return False, f"{path}: expected array, got {type(obj).__name__}"
        items_schema = schema.get("items", {})
        for i, item in enumerate(obj):
            ok, err = validate_value(item, items_schema, f"{path}[{i}]")
            if not ok: return False, err
    return True, None

def validate_value(obj, schema, path=""):
    if "enum" in schema:
        ok, err = validate_enum(obj, schema["enum"], path)
        if not ok: return False, err
    if "$ref" in schema:
        ref_path = schema["$ref"]
        return True, None
    if "type" in schema:
        ok, err = validate_type(obj, schema["type"], path)
        if not ok: return False, err
    if isinstance(schema, dict) and schema.get("type") in ("object", "array") and isinstance(obj, (dict, list)):
        ok, err = validate_schema(obj, schema, path)
        if not ok: return False, err
    return True, None

def validate_state(state, schema):
    if not isinstance(state, dict):
        return False, "state.json must be an object"
    return validate_schema(state, schema)

def _section_key(phase):
    return phase.replace("-", "_")

def check_invariants(state, phases):
    inv = []
    section_key = _section_key(state["phase"])

    inv1_ok = not (state["phase"] == "implement-spec-stage" and state.get(section_key, {}).get("status") == "in_progress")
    if not inv1_ok:
        all_tasks = phases.get("phases", [])
        dev_phase = next((p for p in all_tasks if p["id"] == "implement-spec-stage"), None)
        if dev_phase:
            has_work = any(t["status"] in ("in_progress", "completed") for t in dev_phase.get("tasks", []))
            inv1_ok = has_work
    if not inv1_ok:
        inv.append("INV1: implement-spec-stage active but no tasks in progress/completed")

    if state["phase"] == "write-tests":
        all_tasks = phases.get("phases", [])
        dev_phase = next((p for p in all_tasks if p["id"] == "implement-spec-stage"), None)
        if dev_phase:
            all_done = all(t["status"] == "completed" for t in dev_phase.get("tasks", []))
            if not all_done:
                inv.append("INV2: write-tests phase but not all implement-spec-stage tasks completed")

    if state["status"] == "completed":
        all_tasks = phases.get("phases", [])
        current = next((p for p in all_tasks if p["id"] == state["phase"]), None)
        if current:
            all_done = all(t["status"] == "completed" for t in current.get("tasks", []))
            if not all_done:
                inv.append("INV3: phase completed but not all tasks done")

    if state["status"] == "pending":
        all_tasks = phases.get("phases", [])
        current = next((p for p in all_tasks if p["id"] == state["phase"]), None)
        if current:
            has_work = any(t["status"] == "completed" for t in current.get("tasks", []))
            if has_work:
                inv.append("INV4: phase pending but some tasks completed")

    return inv

def check_entry_gates(state, config):
    phase = state["phase"]
    status = state["status"]
    errors = []
    section_key = phase.replace("-", "_")

    for rule in config.get("phases", []):
        if rule.get("id") != phase:
            continue
        for condition in rule.get("entry", []):
            if condition == "judge: passed":
                section = state.get(section_key, {})
                if section.get("judge_verdict") != "passed":
                    errors.append(f"entry: {phase} requires judge passed")
            elif condition == "questions: 0":
                if len(state.get("questions", {}).get("analyst", [])) > 0:
                    errors.append(f"entry: {phase} requires no open questions")
    return errors

def check_exit_gates(state, config):
    phase = state["phase"]
    status = state["status"]
    errors = []
    section_key = phase.replace("-", "_")

    if status not in ("completed", "failed"):
        return errors

    for rule in config.get("phases", []):
        if rule.get("id") != phase:
            continue
        for condition in rule.get("exit", []):
            if condition == "judge: passed":
                section = state.get(section_key, {})
                if section.get("judge_verdict") != "passed":
                    errors.append(f"exit: {phase} requires judge passed")
            elif condition == "tasks: all_completed":
                tasks = state.get(section_key, {}).get("tasks", [])
                if not all(t["status"] == "completed" for t in tasks):
                    errors.append(f"exit: {phase} needs all tasks completed")
    return errors
