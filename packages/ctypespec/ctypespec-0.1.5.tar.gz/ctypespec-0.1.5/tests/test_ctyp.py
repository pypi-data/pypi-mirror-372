from ctypespec import __version__, ctyp


def verify_ctyp(typ: str, sign: str, category: str, bits: int, short: str):
    ct = ctyp.get(typ)
    print(f"{ct}, {ct.flag}")
    if ct.sign != sign:
        raise ValueError(f"wrong sign: {ct.sign}")
    elif ct.category != category:
        raise ValueError(f"wrong category: {ct.category}")
    elif ct.bits != bits:
        raise ValueError(f"wrong bits: {ct.bits}")
    elif ct.short != short:
        raise ValueError(f"wrong short: {ct.short}")
    elif ct.fmt is None:
        raise ValueError(f"wrong fmt: {ct.fmt}")


print(f"version: {__version__}")
print("----------------")

verify_ctyp("bool", "unsigned", "int", 8, "u8")
verify_ctyp("char", "signed", "int", 8, "i8")
verify_ctyp("int8_t", "signed", "int", 8, "i8")
verify_ctyp("u16", "unsigned", "int", 16, "u16")
verify_ctyp("int32_t", "signed", "int", 32, "i32")
verify_ctyp("float", "signed", "float", 32, "f32")
verify_ctyp("uintptr_t", "unsigned", "pointer", 32, "ptr")
verify_ctyp("unsigned int", "unsigned", "int", 32, "u32")
