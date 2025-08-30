from ctypes import *
from enum import Flag, auto

ctype_fmt_prec = {
    "i8": r"%d",
    "u8": r"%d",
    "i16": r"%d",
    "u16": r"%d",
    "i32": r"%d",
    "u32": r"%d",
    "i64": r"%lld",
    "u64": r"%lld",
    "f32": r"%.6f",
    "f64": r"%.8f",
    "f128": r"%.8f",
    "ptr": r"%ld",
}


class CTypeFlags(Flag):
    NONE = 0

    BIT8 = 8
    BIT16 = 16
    BIT32 = 32
    BIT64 = 64
    BIT128 = 128

    SIGNED = auto()
    UNSIGNED = auto()

    INT = auto()
    FLOAT = auto()
    POINTER = auto()

    BITS = BIT8 | BIT16 | BIT32 | BIT64 | BIT128
    SIGN = SIGNED | UNSIGNED
    CATEGORY = INT | FLOAT | POINTER

    def is_valid(self) -> bool:
        if self & CTypeFlags.POINTER:
            return True
        if self.bit() == 0:
            return False
        return bool(self & CTypeFlags.CATEGORY)

    def is_signed(self) -> bool:
        return bool(self & CTypeFlags.SIGNED)

    def is_unsigned(self) -> bool:
        return bool(self & CTypeFlags.UNSIGNED)

    def is_pointer(self) -> bool:
        return bool(self & CTypeFlags.POINTER)

    def is_integer(self) -> bool:
        return bool(self & CTypeFlags.INT)

    def is_float(self) -> bool:
        return bool(self & CTypeFlags.FLOAT)

    def bit(self) -> int:
        return self.value & CTypeFlags.BITS.value

    def short(self):
        if self & CTypeFlags.POINTER:
            return "ptr"

        # Extract bit size directly without a method call
        bits = self.value & CTypeFlags.BITS.value
        if bits > 0:
            if self & CTypeFlags.INT:
                if self & CTypeFlags.SIGNED:
                    return f"i{bits}"
                elif self & CTypeFlags.UNSIGNED:
                    return f"u{bits}"
            elif self & CTypeFlags.FLOAT:
                return f"f{bits}"

        return None

    def str2value(self, value: str) -> int | float | None:
        if not isinstance(value, str) or self.is_pointer():
            return None
        return int(value) if self.is_integer() else float(value)


_sign_map = {
    "signed": CTypeFlags.SIGNED,
    "unsigned": CTypeFlags.UNSIGNED,
}

_category_map = {
    "int": CTypeFlags.INT,
    "float": CTypeFlags.FLOAT,
    "pointer": CTypeFlags.POINTER,
}

_bits_map = {
    8: CTypeFlags.BIT8,
    16: CTypeFlags.BIT16,
    32: CTypeFlags.BIT32,
    64: CTypeFlags.BIT64,
    128: CTypeFlags.BIT128,
}


class CTypeDescriptor:
    def __init__(self, name: str, sign: str, category: str, bits: int, ctype):  # noqa: C901
        self.name: str = name  # type name
        self.sign: str = sign  # signed | unsigned
        self.category: str = category  # int | float
        self.bits: int = bits  # bit
        self.ctype = ctype  # ctype
        self.bytes: int = bits // 8  # btyes

        self.flag: CTypeFlags = CTypeFlags.NONE
        self.flag |= _sign_map.get(self.sign, CTypeFlags.NONE)
        self.flag |= _category_map.get(self.category, CTypeFlags.NONE)
        self.flag |= _bits_map.get(self.bits, CTypeFlags.NONE)

        self.short: str = self.flag.short()
        self.fmt: str = ctype_fmt_prec.get(self.short)

        max_min_value = self._calc_min_max() if name != "bool" else (0, 1)
        self.min: int | float | None = max_min_value[0]  # min value
        self.max: int | float | None = max_min_value[1]  # max value

    def __str__(self) -> str:
        return (
            f"({self.name}) sign: {self.sign}, category: {self.category}, bits: {self.bits}"
            f", range: [{self.min}, {self.max}], short: {self.short}, fmt: {self.fmt}, ctype: {self.ctype}"
        )

    def _calc_min_max(self) -> tuple[int | float | None, int | float | None]:
        if self.flag.is_integer():
            if self.flag.is_signed():
                return (-(2 ** (self.bits - 1)), 2 ** (self.bits - 1) - 1)
            elif self.flag.is_unsigned():
                return (0, 2**self.bits - 1)
        elif self.flag.is_float():
            if self.bits == CTypeFlags.BIT32:
                return (-3.4e38, 3.4e38)
            elif self.bits == CTypeFlags.BIT64:
                return (-1.7e308, 1.7e308)
            elif self.bits == CTypeFlags.BIT128:
                return (-1.1e4932, 1.1e4932)
        return None, None

    def clip(self, value) -> int | float | None:
        if self.min is None:
            return None
        if value := self.flag.str2value(value):
            return max(self.min, min(value, self.max))
        return None

    def to_value(self, value: str | int | float, clip: bool = False) -> int | float:
        try:
            if isinstance(value, str):
                converted_value = self.flag.str2value(value)
        except ValueError as e:
            return f"Error converting {value} to {self.name}: {e}"
        if clip:
            converted_value = max(self.min, min(converted_value, self.max))
        return converted_value


class CTypeRegistry:
    def __init__(self) -> None:
        self.types: dict[str, CTypeDescriptor] = {}
        self._init_builtin_types()
        self._init_ctype_name_map()

    def _init_builtin_types(self) -> None:
        self.types["wchar"] = CTypeDescriptor("wchar", "signed", "int", 32, c_wchar)

        self.types["char"] = CTypeDescriptor("char", "signed", "int", 8, c_char)  # int8_t
        self.types["signed char"] = CTypeDescriptor("signed char", "signed", "int", 8, c_char)  # int8_t
        self.types["unsigned char"] = CTypeDescriptor("unsigned char", "unsigned", "int", 8, c_ubyte)  # uint8_t

        self.types["short"] = CTypeDescriptor("short", "signed", "int", 16, c_short)  # int16_t
        self.types["signed short"] = CTypeDescriptor("signed short", "signed", "int", 16, c_short)  # int16_t
        self.types["unsigned short"] = CTypeDescriptor("unsigned short", "unsigned", "int", 16, c_ushort)  # uint16_t

        self.types["int"] = CTypeDescriptor("int", "signed", "int", 32, c_int)  # int32_t
        self.types["signed int"] = CTypeDescriptor("signed int", "signed", "int", 32, c_int)  # int32_t
        self.types["unsigned int"] = CTypeDescriptor("unsigned int", "unsigned", "int", 32, c_uint)  # uint32_t

        self.types["long"] = CTypeDescriptor("long", "signed", "int", 64, c_long)  # int64_t
        self.types["signed long"] = CTypeDescriptor("signed long", "signed", "int", 64, c_long)  # int64_t
        self.types["unsigned long"] = CTypeDescriptor("unsigned long", "unsigned", "int", 64, c_ulong)  # uint64_t

        self.types["long int"] = CTypeDescriptor("long int", "signed", "int", 64, c_long)
        self.types["signed long int"] = CTypeDescriptor("signed long int", "signed", "int", 64, c_long)
        self.types["unsigned long int"] = CTypeDescriptor("unsigned long int", "unsigned", "int", 64, c_ulong)

        self.types["long long"] = CTypeDescriptor("long long", "signed", "int", 64, c_long)
        self.types["signed long long"] = CTypeDescriptor("signed long long", "signed", "int", 64, c_long)
        self.types["unsigned long long"] = CTypeDescriptor("unsigned long long", "unsigned", "int", 64, c_ulong)

        self.types["long long int"] = CTypeDescriptor("long long int", "signed", "int", 64, c_long)
        self.types["signed long long int"] = CTypeDescriptor("signed long long int", "signed", "int", 64, c_long)
        self.types["unsigned long long int"] = CTypeDescriptor("unsigned long long int", "unsigned", "int", 64, c_ulong)

        self.types["int8_t"] = CTypeDescriptor("int8_t", "signed", "int", 8, c_char)
        self.types["uint8_t"] = CTypeDescriptor("uint8_t", "unsigned", "int", 8, c_ubyte)
        self.types["int16_t"] = CTypeDescriptor("int16_t", "signed", "int", 16, c_short)
        self.types["uint16_t"] = CTypeDescriptor("uint16_t", "unsigned", "int", 16, c_ushort)
        self.types["int32_t"] = CTypeDescriptor("int32_t", "signed", "int", 32, c_int)
        self.types["uint32_t"] = CTypeDescriptor("uint32_t", "unsigned", "int", 32, c_uint)
        self.types["int64_t"] = CTypeDescriptor("int64_t", "signed", "int", 64, c_long)
        self.types["uint64_t"] = CTypeDescriptor("uint64_t", "unsigned", "int", 64, c_ulong)
        self.types["__int64"] = CTypeDescriptor("__int64", "signed", "int", 64, c_long)
        self.types["signed __int64"] = CTypeDescriptor("signed __int64", "signed", "int", 64, c_long)
        self.types["unsigned __int64"] = CTypeDescriptor("unsigned __int64", "unsigned", "int", 64, c_ulong)

        # self.types["int128_t"] = CTypeDescriptor("int128_t", "signed", "int", 128, c_long)
        # self.types["uint128_t"] = CTypeDescriptor("uint128_t", "unsigned", "int", 128, c_ulong)

        self.types["float32_t"] = CTypeDescriptor("float32_t", "signed", "float", 32, c_float)
        self.types["float64_t"] = CTypeDescriptor("float64_t", "signed", "float", 64, c_double)
        self.types["float128_t"] = CTypeDescriptor("float128_t", "signed", "float", 128, c_longdouble)

        self.types["bool"] = CTypeDescriptor("bool", "unsigned", "int", 8, c_bool)
        self.types["_Bool"] = CTypeDescriptor("bool", "unsigned", "int", 8, c_bool)

        self.types["signed"] = CTypeDescriptor("signed", "signed", "int", 32, c_int)  # int32_t
        self.types["unsigned"] = CTypeDescriptor("unsigned", "unsigned", "int", 32, c_uint)  # uint32_t

        self.types["float"] = CTypeDescriptor("float", "signed", "float", 32, c_float)
        self.types["double"] = CTypeDescriptor("double", "signed", "float", 64, c_double)
        self.types["long double"] = CTypeDescriptor("long double", "signed", "float", 128, c_longdouble)

        self.types["size_t"] = CTypeDescriptor("size_t", "unsigned", "int", 32, c_size_t)  # 32-bit platform

        self.types["void"] = CTypeDescriptor("void", "unsigned", "pointer", 32, c_void_p)  # 32-bit platform
        self.types["uintptr_t"] = CTypeDescriptor("uintptr_t", "unsigned", "pointer", 32, c_void_p)  # 32-bit platform
        self.types["char_ptr"] = CTypeDescriptor("char_ptr", "unsigned", "pointer", 32, c_char_p)  # 32-bit platform
        self.types["wchar_ptr"] = CTypeDescriptor("wchar_ptr", "unsigned", "pointer", 32, c_wchar_p)  # 32-bit platform

        self.types["i8"] = CTypeDescriptor("i8", "signed", "int", 8, c_char)
        self.types["u8"] = CTypeDescriptor("u8", "unsigned", "int", 8, c_ubyte)
        self.types["i16"] = CTypeDescriptor("i16", "signed", "int", 16, c_short)
        self.types["u16"] = CTypeDescriptor("u16", "unsigned", "int", 16, c_ushort)
        self.types["i32"] = CTypeDescriptor("i32", "signed", "int", 32, c_int)
        self.types["u32"] = CTypeDescriptor("u32", "unsigned", "int", 32, c_uint)
        self.types["i64"] = CTypeDescriptor("i64", "signed", "int", 64, c_long)
        self.types["u64"] = CTypeDescriptor("u64", "unsigned", "int", 64, c_ulong)
        self.types["f32"] = CTypeDescriptor("f32", "signed", "float", 32, c_float)
        self.types["f64"] = CTypeDescriptor("f64", "signed", "float", 64, c_double)
        self.types["f128"] = CTypeDescriptor("f128", "signed", "float", 128, c_longdouble)
        self.types["ptr"] = CTypeDescriptor("ptr", "unsigned", "pointer", 32, c_void_p)  # 32-bit platform

    def _init_ctype_name_map(self):
        self.map: dict = {k: v.ctype.__name__ for k, v in self.types.items()}

    def get(self, type_str: str) -> CTypeDescriptor | None:
        return self.types.get(type_str, CTypeDescriptor("unknown", None, None, 0, None))

    def to_ctypes_name(self, type_str: str, _default: str = None) -> str:
        return self.map.get(type_str, _default)


def compute_struct_size(fields: list[dict], alignment: int = 4) -> int:
    sizes = [ctyp.get(v["type"]).bytes for v in fields]

    offset = 0
    for size in sizes:
        align = min(size, alignment)
        if offset % align != 0:
            offset += align - (offset % align)
        offset += size
    if offset % alignment != 0:
        offset += alignment - (offset % alignment)
    return offset


ctyp = CTypeRegistry()
