from enum import IntEnum


class ACT(IntEnum):
    GET = 1
    SET = 2
    ADD = 3
    DEL = 4
    GL = 5
    GS = 6
    OP = 7
    CGI = 8


LINE_BREAK = "\r\n"


def stringify(actions):
    """
    Convert a list of action tuples into a string format with preamble and blocks.
    Each action is a tuple: (type, oid, attributes, stack, pStack).
    """

    def process_action(acc, action, index):
        type_, oid, attributes, stack, pStack = action + (None,) * (5 - len(action))
        stack = stack or "0,0,0,0,0,0"
        pStack = pStack or "0,0,0,0,0,0"

        acc["preamble"].append(str(int(type_)))  # Use numeric value of enum

        if isinstance(attributes, list):
            attribute_lines = attributes
        elif isinstance(attributes, dict):
            attribute_lines = [f"{k}={v}" for k, v in attributes.items()]
        else:
            attribute_lines = []

        header = f"{oid}#{stack}#{pStack}"
        marker = f"{index},{len(attribute_lines)}"
        acc["blocks"].append(LINE_BREAK.join([f"[{header}]{marker}", *attribute_lines]))

        return acc

    result = {"preamble": [], "blocks": []}
    for index, action in enumerate(actions):
        result = process_action(result, action, index)

    return LINE_BREAK.join([",".join(result["preamble"]), *result["blocks"], ""])

def parse_section_header(line):
    """
    Parse a section header line like '[oid#stack#pStack]index,count'.
    """
    end_of_header_index = line.index("]")
    stack = line[1:end_of_header_index]
    trailing_number = int(line[end_of_header_index + 1:].split(",")[0])
    section = {
        "stack": stack,
        "action_index": trailing_number,
    }

    if stack == "cgi":
        return {**section, "script": ""}
    elif stack == "error":
        return {**section, "code": trailing_number}
    else:
        return {**section, "attributes": {}}


def parse_attribute_line(line, section):
    """
    Parse an attribute line like 'key=value' into the section's attributes.
    """
    name, *values = line.split("=", 1)  # Split on first '=' only
    section["attributes"][name] = "=".join(values)


def parse_script_line(line, section):
    """
    Append a line to the section's script field (for CGI sections).
    """
    section["script"] += f"{line}\n"


def parse(data):
    """
    Parse a response string into a structured object with actions and optional error.
    """
    lines = data.split("\n")
    sections = []
    section = None

    for line in lines:
        if line.startswith("["):
            section = parse_section_header(line)
            sections.append(section)
        elif section and section["stack"] == "cgi":
            parse_script_line(line, section)
        elif line and section:
            parse_attribute_line(line, section)

    combined = {"error": None, "actions": []}
    for section in sections:
        if section["stack"] == "error":
            combined["error"] = section["code"]
        else:
            action_index = section["action_index"]
            if action_index >= len(combined["actions"]):
                combined["actions"].extend([None] * (action_index - len(combined["actions"]) + 1))
            if combined["actions"][action_index] is None:
                combined["actions"][action_index] = section
            elif isinstance(combined["actions"][action_index], list):
                combined["actions"][action_index].append(section)
            else:
                combined["actions"][action_index] = [combined["actions"][action_index], section]

    # Fill in any missing action indices with default objects
    for i in range(len(combined["actions"])):
        if combined["actions"][i] is None:
            combined["actions"][i] = {"action_index": i}

    return combined