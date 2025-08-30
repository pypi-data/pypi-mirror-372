import json
import re
from dataclasses import dataclass, field

from .clang_helper import generate_ast_dict, preprocess_headers
from .ctype_helper import ctyp

RE_ARRAY = re.compile(r"\[(\d+)\]")
RE_ARRAY_CLEAN = re.compile(r"\[\d+\]")
RE_ANONYMOUS_TYPE_PATTERN = re.compile(r"^(?P<tag>struct|union|enum) \(unnamed (?P=tag) at (?P<loc>.+?:\d+:\d+)\)$")

ast_type_map = {
    "_Bool": "bool",
}


def remove_ast_tags(node, tags: set[str]):
    """Recursively remove specific tags from AST."""
    if isinstance(node, dict):
        for tag in tags:
            node.pop(tag, None)
        for value in node.values():
            remove_ast_tags(value, tags)
    elif isinstance(node, list):
        for item in node:
            remove_ast_tags(item, tags)


def clean_ast_nodes(ast: dict, include_files: list[str] = None, tags: set = None) -> dict:
    if tags is None:
        tags = {"range", "isImplicit", "isReferenced", "loc"}
    inner = ast.get("inner", [])
    if include_files:
        inner = [node for node in inner if node.get("loc", {}).get("includedFrom", {}).get("file") in include_files]
    remove_ast_tags(inner, tags=tags)
    ast["inner"] = inner
    return ast


def headers_to_ast(
    files: list[str],
    includes: list[str] = None,
    defines: dict[str, any] = None,
    output_dir: str = None,
    output_name: str = None,
    clean: bool = True,
    cwd: str = None,
) -> dict:
    if output_name is None:
        output_name = "header"

    header = preprocess_headers(
        files=files,
        includes=includes,
        defines=defines,
        output_dir=output_dir,
        output_name=output_name,
        cwd=cwd,
    )
    ast = generate_ast_dict(header, output_dir=output_dir)
    if clean:
        ast = clean_ast_nodes(ast, include_files=[str(output_dir / f"{output_name}.h"), *files])

    if output_dir:
        with open(output_dir / "ast.json", "w") as f:
            json.dump(ast, f, indent=2)

    return ast


def is_function_pointer(qualtype: str) -> bool:
    return r"(*)" in qualtype


# def is_anonymous_type(qualtype: str) -> bool:
#     return bool(RE_ANONYMOUS_TYPE_PATTERN.match(qualtype))


def parse_anonymous_record_type(qualtype: str) -> dict:
    match = RE_ANONYMOUS_TYPE_PATTERN.fullmatch(qualtype)
    if not match:
        return None
    return {"type": match.group("tag"), "loc": match.group("loc")}


def parse_qualtype(qualtype: str) -> dict:
    """
    Parse a Clang AST qualType string into structured type info

    Parameters:
        qualtype (str): e.g. "const int *[3][4]", "char **", "volatile float"

    Returns:
        dict: base type info (with pointer depth, qualifiers, array dims)
    """
    qt = qualtype.strip()

    if is_function_pointer(qt):
        return {
            "type": "function",
            "typedef": None,
            "size": (),
            "pointer": 1,
            "qualifiers": [],
            "tokens": [],
        }

    array_dims = tuple(int(dim) for dim in RE_ARRAY.findall(qt))
    qt = RE_ARRAY_CLEAN.sub("", qt)

    pointer_depth = qt.count("*")
    qt = qt.replace("*", "").strip()

    tokens = qt.split()
    qualifiers = [t for t in tokens if t in {"const", "volatile"}]
    tk = [t for t in tokens if t not in qualifiers]

    base = [t for t in tk if t in {"struct", "enum", "union"}]
    if len(base) > 0:
        tk = [t for t in tk if t not in base]
        if len(base) > 1:
            raise ValueError(f"len(base) > 1 ({len(base)})")
        base = base[0]
    else:
        base = None

    tk = " ".join(tk)

    typedef = None
    if tk in ctyp.map or tk in ast_type_map:
        base = ast_type_map.get(tk, tk)
    else:
        typedef = tk

    return {
        "type": base,
        "typedef": typedef,
        "size": array_dims,
        "pointer": pointer_depth,
        "qualifiers": qualifiers,
        "tokens": tokens,
    }


def parse_typedef(node: dict) -> dict:
    inner = node.get("inner", [])
    if not inner:
        return {
            "name": node.get("name"),
            "kind": None,
            "underlying_id": None,
            "underlying_name": None,
            "underlying_type": None,
        }

    underlying_type = node.get("type", {}).get("qualType", "")
    if is_function_pointer(underlying_type):
        # TODO parse function and support "CompareValue, _Bool (void *, void *)"
        return {
            "name": node.get("name"),
            "kind": "function",
            "underlying_id": None,
            "underlying_name": None,
            "underlying_type": None,
        }

    kind = None  # struct / enum / union
    underlying_id = None
    underlying_name = None

    for item in inner:
        owned_tag = item.get("ownedTagDecl", {})
        if owned_tag:
            underlying_id = owned_tag.get("id")
            underlying_name = owned_tag.get("name")
            kind = owned_tag.get("tagUsed")

            if not kind and "type" in item:
                qt = item["type"].get("qualType", "")
                if qt.startswith("struct "):
                    kind = "struct"
                elif qt.startswith("union "):
                    kind = "union"
                elif qt.startswith("enum "):
                    kind = "enum"

    return {
        "name": node.get("name"),
        "kind": kind,
        "underlying_id": underlying_id,
        "underlying_name": underlying_name or None,
        "underlying_type": underlying_type,
    }


def parse_enum(node: dict) -> dict:
    values = {}
    current_value = -1

    inner = node.get("inner", [])
    if not inner:
        return {}

    # get the enum's underlying type from EnumDecl
    enum_type = node.get("type", {}).get("qualType", "int")

    for item in inner:
        if item.get("kind") != "EnumConstantDecl":
            # print(f"item: {item}")
            continue

        if inner_ := item.get("inner"):
            # try to get explicit value
            value_str = inner_[0].get("value")
            if value_str and value_str.isdigit():
                current_value = int(value_str)
        else:
            # auto-increment value
            current_value += 1

        values[item["name"]] = current_value

    return {
        "name": node.get("name"),
        "typedef": None,
        "kind": "enum",
        "type": enum_type,
        "values": values,
    }


def parse_struct(node: dict) -> dict:
    fields = {}

    inner = node.get("inner", [])
    if not inner:
        return {}

    kind = node.get("tagUsed")

    anonymous_types = []
    for item in inner:
        item_kind = item.get("kind")
        if item_kind == "FieldDecl":
            name = item.get("name")

            qualtype = item.get("type", {}).get("qualType", "")
            anonymous = parse_anonymous_record_type(qualtype)
            if anonymous:
                _, last_anonymous_types = anonymous_types[-1]
                qualtype = f"{anonymous['type']} {last_anonymous_types['name']}"

            res = parse_qualtype(qualtype)

            fields[name] = {
                "type": res["type"],
                "typedef": res["typedef"],
                "size": res["size"],
                "pointer": res["pointer"],
                "qualifiers": res["qualifiers"],
            }
        else:
            tag_used = item.get("tagUsed")
            if item_kind == "EnumDecl":
                res = parse_enum(item)
                decl = "Enum"
            elif item_kind == "RecordDecl" and tag_used == "struct":
                res = parse_struct(item)
                decl = "Struct"
            elif item_kind == "RecordDecl" and tag_used == "union":
                # res = parse_union(item)
                res = {"name": None, "typedef": None, "kind": "union", "fields": {}}
                decl = "Union"
            elif item_kind in {"MaxFieldAlignmentAttr", "TypeVisibilityAttr"}:
                # ignore?
                continue
            else:
                raise NotImplementedError(f"kind={item_kind}, tagUsed={tag_used}, {item}")

            id_ = item["id"]
            res["name"] = f"Anonymous{decl}_" + item["id"].split("0x")[-1]
            anonymous_types.append((id_, res))

    return {
        "name": node.get("name"),
        "typedef": None,
        "kind": kind,
        "fields": fields,
        "anonymous_types": anonymous_types,
    }


def find_typedefs_by_underlying_name(typedefs: dict, target_name: str) -> list[dict]:
    return [typedefs[id_] for id_, entry in typedefs.items() if entry["underlying_name"] == target_name]


def find_typedefs_by_underlying_id(typedefs: dict, target_id: str) -> list[dict]:
    return [typedefs[id_] for id_, entry in typedefs.items() if entry["underlying_id"] == target_id]


def find_typedefs_by_name(typedefs: dict, target_name: str) -> list[dict]:
    return [typedefs[id_] for id_, entry in typedefs.items() if entry["name"] == target_name]


def update_field_typedef(fields: dict, typedefs: dict) -> dict:
    fields = fields.copy()
    for name, meta in fields.items():
        if meta["type"] in ctyp.map:
            continue
        typedef = find_typedefs_by_name(typedefs, meta["typedef"])
        if typedef:
            fields[name]["type"] = typedef[0]["kind"]
    return fields


def update_record_typedef(records: dict, typedefs: dict) -> dict:
    records = records.copy()
    for id_ in records:
        name = records[id_]["name"]
        typedef = find_typedefs_by_underlying_id(typedefs, id_)
        if not typedef and name:
            typedef = find_typedefs_by_underlying_name(typedefs, name)
        if typedef:
            typedef = typedef[0]
            if name is None:
                records[id_]["name"] = typedef["underlying_name"]
            records[id_]["typedef"] = typedef["name"]
        if fields := records[id_].get("fields", {}):
            fields = update_field_typedef(fields, typedefs)
            records[id_]["fields"] = fields
    return records


@dataclass
class ASTDecl:
    ast: dict = field(default_factory=dict)
    typedef: dict = field(default_factory=dict)
    struct: dict = field(default_factory=dict)
    enum: dict = field(default_factory=dict)


def parse_ast(ast: dict) -> ASTDecl:
    typedefs = {}
    enums = {}
    structs = {}

    for node in ast.get("inner", []):
        id_ = node["id"]
        kind = node["kind"]

        if kind == "TypedefDecl":
            if res := parse_typedef(node):
                typedefs[id_] = {**res}
        elif kind == "EnumDecl":
            if res := parse_enum(node):
                enums[id_] = {**res}
        elif kind == "RecordDecl":
            if res := parse_struct(node):
                anonymous = res.pop("anonymous_types", [])
                for anonymous_id, anonymous_type in anonymous:
                    if anonymous_type["kind"] == "struct":
                        structs[anonymous_id] = {**anonymous_type}
                    elif anonymous_type["kind"] == "enum":
                        enums[anonymous_id] = {**anonymous_type}
                structs[id_] = {**res}
        # elif kind == "VarDecl":
        #     ...
        # elif kind == "FunctionDecl":
        #     ...
        else:
            ...

    structs = update_record_typedef(structs, typedefs)

    return ASTDecl(ast=ast, typedef=typedefs, struct=structs, enum=enums)
