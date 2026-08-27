"""
Generic rule-evaluation engine for the report builder.

This module has no domain knowledge whatsoever: it only knows how to walk
a small set of declarative "rule" node types (plain dicts with a "type"
key) against a dict of form answers (`fields`) and a table of
already-computed sibling results (`computed`). Every clinically
meaningful detail -- which fields matter, how they combine, what the
cut-offs are, what text explains each answer -- lives in the encrypted
configuration loaded by secure_config.py, never here.

Supported node types:
  const        {"type": "const", "value": X}
  ref          {"type": "ref", "target": "<key already in computed>"}
  if           {"type": "if", "cond": <condition>, "then": <rule>, "else": <rule>}
  switch       {"type": "switch", "on": {"field": ...} | {"var": ...},
                "cases": [{"in": [...], "then": <rule>}, ...],
                "default": <rule> (optional; raises if omitted and no case matches)}
  sum          {"type": "sum", "parts": [<rule>, ...]}
  item_group   {"type": "item_group", "items": [...], "agg": "sum"|"max",
                "map": "<name in value_maps>" | {<inline map>}}
  text_only    {"type": "text_only", "items": [...]}  -- descriptive text only,
                contributes 0 to the numeric value

A condition is either {"var": name, "op": ..., "value": ...} (compares a
derived variable) or {"field": name, "op": ..., "value": ...} (compares a
raw answer). Supported ops: "<", "<=", ">", ">=", "==", "in".
"""


def _cmp(value, op, target):
    if op == "<":
        return value < target
    if op == "<=":
        return value <= target
    if op == ">":
        return value > target
    if op == ">=":
        return value >= target
    if op == "==":
        return value == target
    if op == "in":
        return value in target
    raise ValueError(f"Operador de condição desconhecido: {op}")


def _resolve(spec, fields, variables):
    """Resolve a {"var": ...} or {"field": ...} reference to its value."""
    if "var" in spec:
        return variables[spec["var"]]
    return fields[spec["field"]]


def _eval_condition(cond, fields, variables):
    value = _resolve(cond, fields, variables)
    return _cmp(value, cond["op"], cond["value"])


def evaluate(rule, fields, variables, rel_items, value_maps, computed):
    """
    Evaluate one rule node.

    Returns (numeric_value, report_sentence).
    """
    node_type = rule["type"]

    if node_type == "const":
        return rule["value"], ""

    if node_type == "ref":
        return computed[rule["target"]]

    if node_type == "if":
        branch = rule["then"] if _eval_condition(rule["cond"], fields, variables) else rule["else"]
        return evaluate(branch, fields, variables, rel_items, value_maps, computed)

    if node_type == "switch":
        current = _resolve(rule["on"], fields, variables)
        for case in rule["cases"]:
            if current in case["in"]:
                return evaluate(case["then"], fields, variables, rel_items, value_maps, computed)
        if "default" in rule:
            return evaluate(rule["default"], fields, variables, rel_items, value_maps, computed)
        raise ValueError(f"Nenhum caso de 'switch' corresponde ao valor {current!r}")

    if node_type == "sum":
        total = 0
        sentences = []
        for part in rule["parts"]:
            value, sentence = evaluate(part, fields, variables, rel_items, value_maps, computed)
            total += value
            if sentence:
                sentences.append(sentence)
        return total, "\n".join(sentences)

    if node_type == "item_group":
        raw_map = rule["map"]
        value_map = raw_map if isinstance(raw_map, dict) else value_maps[raw_map]
        values = [value_map[fields[item]] for item in rule["items"]]
        total = max(values) if rule["agg"] == "max" else sum(values)
        # rel_items comes from decoded JSON, so its per-code keys are strings
        # ("0", "1", ...) even though the field values already are strings too.
        sentence = "\n".join(rel_items[item][str(fields[item])] for item in rule["items"])
        return total, sentence

    if node_type == "threshold_bool":
        matched = _cmp(int(fields[rule["field"]]), rule["op"], rule["value"])
        return (rule["score"] if matched else 0), ""

    if node_type == "text_only":
        sentence = "\n".join(f"{rel_items[item]}: {fields[item]}." for item in rule["items"])
        return 0, sentence

    raise ValueError(f"Tipo de regra desconhecido: {node_type!r}")
