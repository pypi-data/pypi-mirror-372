"""
Nosfuscate main classes
"""

import base64
import logging
import random

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.ciphers import Cipher, modes

LOGGER = logging.getLogger(__name__)


class Cisco:
    """
    Implementation of the classic Cisco type 7 obfuscation
    """

    XLAT: bytes = "dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv".encode("ASCII")

    def type7_decode(self, crypt: str) -> str:
        """
        Decrypt a Cisco tyye 7 obfuscated password
        """
        if len(crypt) < 2 or (len(crypt) % 2 != 0):
            raise ValueError("Invalid type 7 password")

        try:
            index = int(crypt[0:2])
        except ValueError as exc:
            raise ValueError("Invalid type 7 password") from exc

        if not (0 <= index < 16):
            raise ValueError("Invalid type 7 password")

        res = ""
        for char in bytes.fromhex(crypt[2:]):
            res += chr(char ^ self.XLAT[index])
            index += 1

        return res

    def type7_encode(self, plain: str, *, salt: int | None = None) -> str:
        """
        Encrypt a Cisco type 7 obfuscated password
        """

        if len(plain) > 25:
            raise ValueError("Input must not be longer than 25 characters")

        if salt is not None:
            if not (0 <= salt < 16):
                raise ValueError("Invalid salt, must be between 0 and 15")
            index = salt
        else:
            index = random.randint(0, 15)
        res = f"{index:02d}"

        for char in plain:
            res += f"{(ord(char) ^ self.XLAT[index]):02X}"
            index += 1

        return res


class Arista:
    """
    Implementation of Arista EOS type 7 obfuscation.
    Mostly follows the implementation in
    https://github.com/aristanetworks/avd.git, which itself follows
    https://github.com/isotopp/arista_type_7/blob/main/pypoc.py

    The code in this class is provided under the Apache-2.0 license.
    """

    SEED = b"\xd5\xa8\xc9\x1e\xf5\xd5\x8a\x23"
    PARITY_BITS = [
        0x01,
        0x01,
        0x02,
        0x02,
        0x04,
        0x04,
        0x07,
        0x07,
        0x08,
        0x08,
        0x0B,
        0x0B,
        0x0D,
        0x0D,
        0x0E,
        0x0E,
        0x10,
        0x10,
        0x13,
        0x13,
        0x15,
        0x15,
        0x16,
        0x16,
        0x19,
        0x19,
        0x1A,
        0x1A,
        0x1C,
        0x1C,
        0x1F,
        0x1F,
        0x20,
        0x20,
        0x23,
        0x23,
        0x25,
        0x25,
        0x26,
        0x26,
        0x29,
        0x29,
        0x2A,
        0x2A,
        0x2C,
        0x2C,
        0x2F,
        0x2F,
        0x31,
        0x31,
        0x32,
        0x32,
        0x34,
        0x34,
        0x37,
        0x37,
        0x38,
        0x38,
        0x3B,
        0x3B,
        0x3D,
        0x3D,
        0x3E,
        0x3E,
        0x40,
        0x40,
        0x43,
        0x43,
        0x45,
        0x45,
        0x46,
        0x46,
        0x49,
        0x49,
        0x4A,
        0x4A,
        0x4C,
        0x4C,
        0x4F,
        0x4F,
        0x51,
        0x51,
        0x52,
        0x52,
        0x54,
        0x54,
        0x57,
        0x57,
        0x58,
        0x58,
        0x5B,
        0x5B,
        0x5D,
        0x5D,
        0x5E,
        0x5E,
        0x61,
        0x61,
        0x62,
        0x62,
        0x64,
        0x64,
        0x67,
        0x67,
        0x68,
        0x68,
        0x6B,
        0x6B,
        0x6D,
        0x6D,
        0x6E,
        0x6E,
        0x70,
        0x70,
        0x73,
        0x73,
        0x75,
        0x75,
        0x76,
        0x76,
        0x79,
        0x79,
        0x7A,
        0x7A,
        0x7C,
        0x7C,
        0x7F,
        0x7F,
    ]
    ENC_SIG = b"\x4c\x88\xbb"

    def _des_setparity(self, key: bytearray) -> bytes:
        res = b""
        for b in key:
            pos = b & 0x7F
            res += self.PARITY_BITS[pos].to_bytes(1, byteorder="big")
        return res

    def _hashkey(self, pw: bytes) -> bytes:
        result = bytearray(self.SEED)

        for idx, b in enumerate(pw):
            result[idx & 7] ^= b

        return bytes(self._des_setparity(result))

    def _cbc_decrypt(self, crypt: str, key: str) -> str:
        crypt_b = crypt.encode("utf-8")
        key_b = key.encode("utf-8")

        data = base64.b64decode(crypt_b)
        hashed_key = self._hashkey(key_b)

        cipher = Cipher(TripleDES(hashed_key), modes.CBC(bytes(8)), default_backend())
        decryptor = cipher.decryptor()
        result = decryptor.update(data)
        decryptor.finalize()

        pad = result[3] >> 4
        if result[:3] != self.ENC_SIG or pad >= 8 or len(result[4:]) < pad:
            raise ValueError("Invalid Encrypted String")
        password_len = len(result) - pad
        return result[4:password_len].decode("utf-8")

    def _cbc_encrypt(self, plain: str, key: str) -> str:
        plain_b = plain.encode("utf-8")
        key_b = key.encode("utf-8")

        hashed_key = self._hashkey(key_b)
        padding = (8 - ((len(plain_b) + 4) % 8)) % 8
        ciphertext = (
            self.ENC_SIG + bytes([padding * 16 + 0xE]) + plain_b + bytes(padding)
        )

        cipher = Cipher(TripleDES(hashed_key), modes.CBC(bytes(8)), default_backend())
        encryptor = cipher.encryptor()
        result = encryptor.update(ciphertext)
        encryptor.finalize()

        return base64.b64encode(result).decode("utf-8")

    def type7_decode(self, crypt: str, key: str) -> str:
        """
        Decode an Arista type 7 obfuscated password.
        `key` is a string that is used to deobfuscate the password. Its
        value is dependent on the context the password is used in.

        * For BGP MD5 auth, the key is the neighbor IP (if not using groups)
          or the group name, followed by `_passwd`. For example, for a neighbor
          of 1.2.3.4 the key would be `1.2.3.4_passwd`.
        * For OSPF simple authentication, the key is the interface name,
          followed by `_passwd`. For example, for simple authentication for
          OSPF on interface Ethernet1 the key would be `Ethernet1_passwd`.
        """

        return self._cbc_decrypt(crypt, key)

    def type7_encode(self, plain: str, key: str) -> str:
        """
        Encode an Arista type 7 obfuscated password.
        `key` is a string that is used to obfuscate the password. Its
        value is dependent on the context the password is used in.

        * For BGP MD5 auth, the key is the neighbor IP (if not using groups)
          or the group name, followed by `_passwd`. For example, for a neighbor
          of 1.2.3.4 the key would be `1.2.3.4_passwd`.
        * For OSPF simple authentication, the key is the interface name,
          followed by `_passwd`. For example, for simple authentication for
          OSPF on interface Ethernet1 the key would be `Ethernet1_passwd`.
        """

        return self._cbc_encrypt(plain, key)


class Juniper:
    """
    This is a pretty straight forward port of the code at
    https://metacpan.org/release/KBRINT/Crypt-Juniper-0.02/source/lib/Crypt/Juniper.pm
    Some changes have been made for a more python-y
    feel, but the general structure has been kept

    The code in this class is provided under the Artistic-1.0 or GPL v1 or later
    license.
    """

    FAMILY: tuple[str, ...] = (
        "QzF3n6/9CAtpu0O",
        "B1IREhcSyrleKvMW8LXx",
        "7N-dVbwsY2g4oaJZGUDj",
        "iHkq.mPf5T",
    )
    EXTRA: dict[str, int] = {}
    ENCODING: tuple[tuple[int, ...], ...] = (
        (1, 4, 32),
        (1, 16, 32),
        (1, 8, 32),
        (1, 64),
        (1, 32),
        (1, 4, 16, 128),
        (1, 32, 64),
    )
    NUM_ALPHA: tuple[str, ...] = tuple(x for x in "".join(FAMILY))
    ALPHA_NUM: dict[str, int] = {x: idx for idx, x in enumerate(NUM_ALPHA)}

    def __init__(self) -> None:
        for idx, entry in enumerate(self.FAMILY):
            for char in entry:
                self.EXTRA[char] = 3 - idx

    def _gap(self, char1: str, char2: str) -> int:
        return (
            (self.ALPHA_NUM[char2] - self.ALPHA_NUM[char1]) % len(self.NUM_ALPHA)
        ) - 1

    def _gap_decode(self, gaps: list[int], dec: tuple[int, ...]) -> str:
        if len(gaps) != len(dec):
            raise ValueError(f"{gaps=} and {dec=} must be the same length")
        num = 0
        for idx, entry in enumerate(gaps):
            num += entry * dec[idx]

        return chr(num % 256)

    def _gap_encode(self, char: str, prev: str, encode: tuple[int, ...]) -> str:
        ordinal = ord(char)

        crypt = ""
        gaps: list[int] = []

        for mod in reversed(encode):
            gaps = [ordinal // mod] + gaps
            ordinal %= mod

        for gap in gaps:
            gap += self.ALPHA_NUM[prev] + 1
            prev = self.NUM_ALPHA[gap % len(self.NUM_ALPHA)]
            crypt += prev

        return crypt

    def type9_decode(self, crypt: str) -> str:
        """
        De-obfuscate the JunOS tye 9 string `crypt`
        """
        if not crypt.startswith("$9$"):
            raise ValueError(f"{crypt=} is not a valid obfuscated JunOS secret")
        chars = crypt[3:]

        first, chars = chars[0], chars[1:]
        if first not in self.EXTRA:
            raise ValueError(
                f"{crypt=} is not a valid obfuscated JunOS secret (invalid salt"
            )
        chars = chars[self.EXTRA[first] :]

        prev = first
        decrypt: str = ""

        while len(chars) > 0:
            decode = self.ENCODING[len(decrypt) % len(self.ENCODING)]
            length = len(decode)
            if len(chars) < length:
                raise ValueError(
                    f"{crypt=} is not a valid obfuscated JunOS secret (truncated?)"
                )
            nibble, chars = chars[0:length], chars[length:]
            gaps: list[int] = []
            for entry in nibble:
                gaps.append(self._gap(prev, entry))
                prev = entry

            decrypt += self._gap_decode(gaps, decode)

        return decrypt

    def type9_encode(
        self, plain: str, *, salt: str | None = None, rand: str | None = None
    ) -> str:
        """
        Obfuscate the string `plain` using `salt` (a single character)
        and `rand` (a 3 character string). `salt` and `rand` can
        be given if you want to re-create a specific obfuscated string
        from a plain text.
        Depending on `salt`, not all characters from `rand` may be used.
        """
        if salt is None:
            salt = random.choice(self.NUM_ALPHA)
        elif len(salt) != 1:
            raise ValueError("Salt must be a single character")

        if salt not in self.EXTRA:
            raise ValueError("Invalid salt")

        if rand is None:
            rand = "".join(random.choices(self.NUM_ALPHA, k=self.EXTRA[salt]))
        else:
            if len(rand) != 3:
                raise ValueError("Invalid length of rand")
            rand = rand[: self.EXTRA[salt]]
            for char in rand:
                if char not in self.EXTRA:
                    raise ValueError("Invalid characters in rand")

        pos = 0
        prev = salt
        crypt = "$9$" + salt + rand

        for char in plain:
            encode = self.ENCODING[pos % len(self.ENCODING)]
            crypt += self._gap_encode(char, prev, encode)
            prev = crypt[-1]
            pos += 1

        return crypt
