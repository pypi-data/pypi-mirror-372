# Copyright (C) 2022 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility classes for converting between byte representations."""
import datetime
import struct
from abc import ABC, abstractmethod
from decimal import Decimal
from functools import lru_cache
from typing import Any, Callable, Tuple


class _Packer(ABC):
    def pack(self, element: Any) -> bytes:
        try:
            element = self._caster(element)
        except Exception:
            raise ValueError(
                f"Could not cast value {element} with caster {self._caster}."
            )

        self._validator(element)
        return struct.pack(self._format_code, self._caster(element))

    def unpack(self, raw_bytes: bytes, start_idx: int) -> Tuple[Any, int]:
        element_bytes = raw_bytes[start_idx : start_idx + self._element_size]
        [parsed_element] = struct.unpack(self._format_code, element_bytes)

        self._validator(parsed_element)
        return self._caster(parsed_element), self._element_size

    @property
    @abstractmethod
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def _caster(self) -> Callable:
        """Get the method for casting the element."""
        raise NotImplementedError()

    @staticmethod
    def _unpack_sized_blob(blob: bytes, start_idx: int) -> Tuple[bytes, int]:
        element_size, integer_size = _UnsignedIntegerPacker().unpack(blob, start_idx)
        return (
            blob[start_idx + integer_size : start_idx + integer_size + element_size],
            element_size + integer_size,
        )

    @abstractmethod
    def _validator(self, element: Any) -> None:
        """Validate the data."""
        raise NotImplementedError()


class _BoolPacker(_Packer):
    _element_size = 1
    _format_code = "?"
    _caster = bool

    def _validator(self, element: Any) -> None:
        # No additional validation needed for booleans
        pass


class _IntegerPacker(_Packer):
    _element_size = 4
    _format_code = "i"
    _caster = int
    _signed = True

    def _validator(self, element: Any) -> None:
        """Validate the data."""
        _validate_integer(element, self._element_size * 8, self._signed)


class _BytePacker(_IntegerPacker):
    _element_size = 1
    _format_code = "B"
    _caster = int
    _signed = False


class _Int16Packer(_IntegerPacker):
    _element_size = 2
    _format_code = "h"
    _caster = int


class _UnsignedIntegerPacker(_IntegerPacker):
    _element_size = 4
    _format_code = "I"
    _caster = int
    _signed = False


class _LongIntegerPacker(_IntegerPacker):
    _element_size = 8
    _format_code = "q"
    _caster = int


class _FloatPacker(_Packer):
    _element_size = 4
    _format_code = "f"
    _caster = float

    def _validator(self, element: Any) -> None:
        _validate_float(element, 1e38, 3.4)


class _DoublePacker(_Packer):
    _element_size = 8
    _format_code = "d"
    _caster = float

    def _validator(self, element: Any) -> None:
        _validate_float(element, 1e308, 1.7)


class _StringPacker(_Packer):
    def pack(self, string: str) -> bytes:
        string = str(string)
        self._validator(string)

        string_bytes = string.encode("utf-8")
        string_size = len(string_bytes)

        return _UnsignedIntegerPacker().pack(string_size) + string_bytes

    def unpack(self, raw_bytes: bytes, start_idx: int) -> Tuple[str, int]:
        blob, element_size = self._unpack_sized_blob(raw_bytes, start_idx)

        string = blob.decode("utf-8")
        self._validator(string)
        return string, element_size

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for strings
        pass


class _DatePacker(_StringPacker):
    def _validator(self, element: Any) -> None:
        super()._validator(element)
        datetime.datetime.strptime(element, "%Y-%m-%d")


class _DatetimePacker(_StringPacker):
    def _validator(self, element: Any) -> None:
        super()._validator(element)
        datetime.datetime.strptime(element, "%Y-%m-%d %H:%M:%S")


class _BlobPacker(_Packer):
    def pack(self, blob: bytes) -> bytes:
        blob = bytes(blob)
        self._validator(blob)
        return _UnsignedIntegerPacker().pack(len(blob)) + blob

    def unpack(self, raw_bytes: bytes, start_idx: int) -> Tuple[bytes, int]:
        blob, size = self._unpack_sized_blob(raw_bytes, start_idx)
        self._validator(blob)
        return blob, size

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for blobs
        pass


class _IndirectStringPacker(_Packer):
    @classmethod
    def pack(cls, string: str) -> bytes:
        return bytes()

    @classmethod
    def unpack(cls, raw_bytes: bytes, start_idx: int) -> Tuple[str, int]:
        return "", 0

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for indirect strings
        pass


class _IndirectBlobPacker(_Packer):
    @classmethod
    def pack(cls, blob: bytes) -> bytes:
        return bytes()

    @classmethod
    def unpack(cls, raw_bytes: bytes, start_idx: int) -> Tuple[bytes, int]:
        return bytes(), 0

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for indirect blobs
        pass


class _BoolTruePacker(_Packer):
    @classmethod
    def pack(cls, element: bool) -> bytes:
        return bytes()

    @classmethod
    def unpack(cls, raw_bytes: bytes, start_idx: int) -> Tuple[bool, int]:
        return True, 0

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for boolean true types
        pass


class _BoolFalsePacker(_Packer):
    @classmethod
    def pack(cls, element: bool) -> bytes:
        return bytes()

    @classmethod
    def unpack(cls, raw_bytes: bytes, start_idx: int) -> Tuple[bool, int]:
        return False, 0

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for boolean false types
        pass


class _EmptyStringPacker(_Packer):
    @classmethod
    def pack(cls, element: str) -> bytes:
        return bytes()

    @classmethod
    def unpack(cls, raw_bytes: bytes, start_idx: int) -> Tuple[str, int]:
        return "", 0

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for empty strings
        pass


class _NullPacker(_Packer):
    @classmethod
    def pack(cls, element: str) -> bytes:
        return bytes()

    @classmethod
    def unpack(cls, raw_bytes: bytes, start_idx: int) -> Tuple[None, int]:
        return None, 0

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for nulls
        pass


class _Int0Packer(_Packer):
    @classmethod
    def pack(cls, element: str) -> bytes:
        return bytes()

    @classmethod
    def unpack(cls, raw_bytes: bytes, start_idx: int) -> Tuple[int, int]:
        return 0, 0

    @property
    def _format_code(self) -> str:
        """Get the format code for struct package."""
        raise NotImplementedError()

    @property
    def _element_size(self) -> int:
        """Get the element size (in bytes) of the packer."""
        raise NotImplementedError()

    @property
    def _caster(self) -> int:
        """Get the method for casting the element."""
        raise NotImplementedError()

    def _validator(self, element: Any) -> None:
        # No additional validation needed for int 0
        pass


def _validate_integer(element: Any, num_bits: int, signed: bool) -> None:
    """Validate whether this integer is in bounds given it's AMPFieldType."""
    max_val = max_int(num_bits, signed)
    min_val = min_int(num_bits, signed)

    if element < min_val or element > max_val:
        raise ValueError(
            f"{'Signed' if signed else 'Unsigned'} integer with {num_bits} bits must fall in the range of {min_val} to {max_val}."
        )


def _validate_float(element: Any, exp, digit) -> None:
    """Validate whether this float is in bounds given it's AMPFieldType."""
    # TODO potentially validate for floats with exponent less than -38 and for doubles with exponent less than -308
    limit = float_limit(exp, digit)
    dec_element = Decimal(str(element))

    if dec_element < -limit or dec_element > limit:
        raise ValueError(f"Float must fall in the range of -{limit} to {limit}.")


@lru_cache()
def min_int(num_bits: int, signed: bool) -> int:
    """Calculate the minimum value that an integer can be considering it's bit length and whether it is signed."""
    return signed * -1 * (2 ** (num_bits - 1))


@lru_cache()
def max_int(num_bits: int, signed: bool) -> int:
    """Calculate the maximum value that an integer can be considering it's bit length and whether it is signed."""
    return 2 ** (num_bits - (1 * signed)) - 1


@lru_cache()
def float_limit(exp: float, digit: float) -> "Decimal":
    """Calculate the limit of a float given it's exponent and digit."""
    return Decimal(str(exp)) * Decimal(str(digit))
