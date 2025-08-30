import json
from itertools import product

from .ast_parser import ASTDecl
from .ctype_helper import ctyp

record_ctype_map = {
    "struct": "Structure",
    "union": "Union",
}


def decl_to_cobj(decl: ASTDecl, output_file: str = None) -> dict:
    ctype = {}

    for enum in decl.enum.values():
        name = enum.get("typedef") or enum.get("name")
        if name is None:
            continue

        ctype[name] = {
            "kind": "enum",
            "type": enum.get("type"),
            "fields": enum.get("values", {}),
        }

    for struct in decl.struct.values():
        name = struct.get("typedef") or struct.get("name")
        if name is None:
            continue

        ctype[name] = {
            "kind": "struct",
            "fields": struct.get("fields"),
        }

    if output_file:
        with open(output_file, "w") as f:
            f.write(json.dumps(ctype, indent=2, ensure_ascii=False))

    return ctype


def expand_cobj(cobj: dict, output_file: str = None) -> dict[str, list[dict]]:
    structs = {k: v["fields"] for k, v in cobj.items() if v.get("kind") == "struct"}
    enums = {k: v["type"] for k, v in cobj.items() if v.get("kind") == "enum"}

    def generate_indices(sizes: list[int]) -> list[str]:
        if not sizes:
            return [""]
        return ["".join(f"[{i}]" for i in idx) for idx in product(*[range(s) for s in sizes])]

    def expand_field(field: dict, name: str, prefix: str = "", parent_is_pointer: bool = None) -> list[dict]:
        full_name = f"{prefix}{name}" if prefix else name
        type_ = field["type"]
        typedef = field.get("typedef")
        pointer = field.get("pointer", 0)
        size = field.get("size", [])
        indices = generate_indices(size)

        fields = []
        if type_ == "struct" and typedef in structs:
            for idx in indices:
                for sub_name, sub_field in structs[typedef].items():
                    sub_prefix = f"{full_name}{idx}."
                    fields.extend(expand_field(sub_field, sub_name, prefix=sub_prefix, parent_is_pointer=(pointer > 0)))
        elif type_ == "enum":
            enum_type = enums.get("typedef", {}).get("type", "int")
            for idx in indices:
                fields.append(
                    {
                        "name": f"{full_name}{idx}",
                        "type": enum_type,
                        "pointer": pointer,
                    }
                )
        else:
            for idx in indices:
                if parent_is_pointer:
                    parts = full_name.rsplit(".", 1)
                    if len(parts) == 2:
                        full_name = "->".join(parts)
                fields.append(
                    {
                        "name": f"{full_name}{idx}",
                        "type": type_,
                        "pointer": pointer,
                    }
                )
        return fields

    cobj_ex = {
        typename: [item for field_name, field in fields.items() for item in expand_field(field, field_name)]
        for typename, fields in structs.items()
    }

    if output_file:
        with open(output_file, "w") as f:
            f.write(json.dumps(cobj_ex, indent=2, ensure_ascii=False))

    return cobj_ex


def get_record_name(record: dict) -> str:
    return record["typedef"] or record["name"]


def decl_to_ctypes(decl: ASTDecl, output_file: str = None) -> str:
    # TODO union

    structs = decl.struct

    import_content = ["from ctypes import *", ""]
    # forward_content = ["# Forward declarations"]
    # definition_content = ["# Full definitions"]
    forward_content = []
    definition_content = []

    # forward declarations
    for struct in structs.values():
        record_name = get_record_name(struct)
        if not record_name:
            continue
        record_kind = record_ctype_map.get(struct.get("kind"))
        forward_content.append(f"\nclass {record_name}({record_kind}):\n    pass\n")

    # full definitions
    for struct in structs.values():
        record_name = get_record_name(struct)
        if not record_name:
            continue

        fields = struct.get("fields")
        if not fields:
            continue

        lines = []
        for name, meta in struct.get("fields", {}).items():
            type_ = meta.get("type")
            if type_ in {None, "struct", "union"}:
                base = meta.get("typedef")
            elif type_ == "enum":
                base = "int"
            else:
                base = type_

            ctype_str = ctyp.map.get(base, base)

            pointer = meta.get("pointer", 0)
            for _ in range(pointer):
                ctype_str = f"POINTER({ctype_str})"

            size = meta.get("size", [])
            for dim in reversed(size):
                ctype_str = f"{ctype_str} * {dim}"

            lines.append(f'        ("{name}", {ctype_str}),')

        record_kind = record_ctype_map.get(struct.get("kind"))

        definition_content.append(f"\nclass {record_name}({record_kind}):  # noqa: F811")
        definition_content.append("    _fields_ = [")
        definition_content.extend(lines)
        definition_content.append("    ]\n")

    content = "\n".join(import_content + forward_content + definition_content)

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)

    return content
