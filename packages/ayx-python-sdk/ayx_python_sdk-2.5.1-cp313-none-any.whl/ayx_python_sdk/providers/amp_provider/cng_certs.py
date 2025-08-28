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
# type: ignore
"""READ cert/private key from windows STORE."""


from ctypes import (
    POINTER,
    Structure,
    WinDLL,
    c_char_p,
    c_ulong,
    c_void_p,
    cast,
    create_string_buffer,
    pointer,
    string_at,
)
from ctypes.wintypes import BYTE, DWORD, LPCWSTR
from typing import Optional, Tuple

import wincertstore as wcs

if wcs.USE_LAST_ERROR:
    Ncrypt = WinDLL("Ncrypt.dll", use_last_error=True)
else:
    Ncrypt = WinDLL("Ncrypt.dll")

NCRYPT_KEY_HANDLE = c_void_p

NCRYPT_PROV_HANDLE = c_void_p

NCryptOpenStorageProvider = Ncrypt.NCryptOpenStorageProvider
NCryptOpenStorageProvider.argtypes = [POINTER(NCRYPT_PROV_HANDLE), LPCWSTR, DWORD]
NCryptOpenStorageProvider.restype = DWORD

MS_KEY_STORAGE_PROVIDER = "Microsoft Software Key Storage Provider"

NCryptOpenKey = Ncrypt.NCryptOpenKey
NCryptOpenKey.argtypes = [
    NCRYPT_PROV_HANDLE,
    POINTER(NCRYPT_KEY_HANDLE),
    LPCWSTR,
    DWORD,
    DWORD,
]
NCryptOpenKey.restype = DWORD


BCRYPT_RSAFULLPRIVATE_BLOB = "RSAFULLPRIVATEBLOB"
CNG_RSA_PRIVATE_KEY_BLOB = 83
SZOID_RSA_RSA = "1.2.840.113549.1.1.1"
X509_ASN_ENCODING = 1
CRYPT_ENCODE_ALLOC_FLAG = 0x8000
PKCS_PRIVATE_KEY_INFO = 44

NCryptExportKey = Ncrypt.NCryptExportKey
NCryptExportKey.argtypes = [
    NCRYPT_KEY_HANDLE,
    NCRYPT_KEY_HANDLE,
    LPCWSTR,
    c_void_p,
    POINTER(BYTE),
    DWORD,
    POINTER(DWORD),
    DWORD,
]
NCryptExportKey.restype = DWORD


class CryptPrivateKeyInfo(Structure):
    """Docstring."""

    __slots__ = ()
    _fields_ = [
        ("Version", DWORD),
        # CRYPT_ALGORITHM_IDENTIFIER/Algorithm
        ("pszObjId", c_char_p),
        # CRYPT_ALGORITHM_IDENTIFIER.CRYPT_OBJID_BLOB
        ("algoCbData", DWORD),
        ("algoPbData", POINTER(BYTE)),
        # CRYPT_DER_BLOB/PrivateKey
        ("pkeyCbData", DWORD),
        ("pkeyPbData", POINTER(BYTE)),
        ("pAttributes", c_void_p),
    ]


CryptEncodeObjectEx = wcs.crypt32.CryptEncodeObjectEx
CryptEncodeObjectEx.argtypes = [
    DWORD,
    c_void_p,
    c_void_p,
    DWORD,
    c_void_p,
    POINTER(c_void_p),
    POINTER(DWORD),
]
CryptEncodeObjectEx.restype = DWORD


class PrivateKeyPem(wcs.ContextStruct):
    """Docstring."""

    cert_type = "PRIVATE KEY"
    # WARNING: please DO NOT CHANGE THIS VARIABLE NAME: it is used in wincertstore
    dwCertEncodingType = 0  # noqa
    # End warning

    def __init__(self, pb_key: c_void_p, cb_key: c_ulong) -> None:
        self.pb_key = pb_key
        self.cb_key = cb_key

    def get_encoded(self) -> bytes:
        """Docstring."""
        return string_at(self.pb_key, self.cb_key.value)


def read_windows_store_chain(cert_name: str) -> Optional[Tuple[bytes, bytes]]:
    """Docstring."""
    with wcs.CertSystemStore("MY") as store:
        for cert in store.itercerts(usage=wcs.SERVER_AUTH):
            if (
                cert.get_name() == "localhost"
                and cert.get_name(wcs.CERT_NAME_FRIENDLY_DISPLAY_TYPE) == cert_name
            ):
                certpem = cert.get_pem()
                provider_handle = NCRYPT_PROV_HANDLE()
                NCryptOpenStorageProvider(provider_handle, MS_KEY_STORAGE_PROVIDER, 0)
                key_handle = NCRYPT_KEY_HANDLE()
                NCryptOpenKey(provider_handle, key_handle, cert_name, 0, 0)
                cb_key = DWORD()
                NCryptExportKey(
                    key_handle,
                    None,
                    BCRYPT_RSAFULLPRIVATE_BLOB,
                    None,
                    None,
                    0,
                    cb_key,
                    0,
                )
                pb_key = create_string_buffer(cb_key.value)
                NCryptExportKey(
                    key_handle,
                    None,
                    BCRYPT_RSAFULLPRIVATE_BLOB,
                    None,
                    cast(pb_key, POINTER(BYTE)),
                    cb_key.value,
                    cb_key,
                    0,
                )

                private_key_info = CryptPrivateKeyInfo()
                private_key_info.Version = 0
                private_key_info.pszObjId = SZOID_RSA_RSA.encode("utf-8")

                enc1_cb_key = DWORD()
                enc1_pb_key = c_void_p()
                CryptEncodeObjectEx(
                    X509_ASN_ENCODING,
                    cast(CNG_RSA_PRIVATE_KEY_BLOB, c_void_p),
                    pb_key,
                    CRYPT_ENCODE_ALLOC_FLAG,
                    None,
                    enc1_pb_key,
                    enc1_cb_key,
                )
                private_key_info.pkeyCbData = enc1_cb_key
                private_key_info.pkeyPbData = cast(enc1_pb_key, POINTER(BYTE))
                enc_cb_key = DWORD()
                enc_pb_key = c_void_p()
                CryptEncodeObjectEx(
                    X509_ASN_ENCODING,
                    cast(PKCS_PRIVATE_KEY_INFO, c_void_p),
                    pointer(private_key_info),
                    CRYPT_ENCODE_ALLOC_FLAG,
                    None,
                    enc_pb_key,
                    enc_cb_key,
                )
                pkp = PrivateKeyPem(enc_pb_key, enc_cb_key)
                keypem = pkp.get_pem()
                return bytes(keypem, "utf-8"), bytes(certpem, "utf-8")
    return None
