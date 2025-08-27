from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import math


@dataclass(slots=True)
class Griffinere:
    key: str
    alphabet: str | None = None

    _alphabet: List[str] = field(init=False, repr=False)
    _alphabet_length: int = field(init=False, repr=False)
    _alphabet_position_map: Dict[str, int] = field(init=False, repr=False)
    _key_chars: List[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        default_alphabet = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789"
        )
        alphabet_str = self.alphabet or default_alphabet
        self._alphabet = self._validate_alphabet(alphabet_str)
        self._alphabet_length = len(self._alphabet)
        self._alphabet_position_map = {ch: idx for idx, ch in enumerate(self._alphabet)}
        self._validate_key(self.key, self._alphabet)
        self._key_chars = list(self.key)

    # -------------------------
    # Public API
    # -------------------------

    def encrypt_string(self, plain_text: str, minimum_response_length: int | None = None) -> str:
        if not plain_text or plain_text.isspace():
            return ""

        if minimum_response_length is None:
            return self._encrypt_segments(plain_text)

        if minimum_response_length < 1:
            raise ValueError("minimum_response_length must be greater than zero")

        need_to_add = minimum_response_length - len(plain_text)
        if need_to_add <= 0:
            return self._encrypt_segments(plain_text)

        pull_from_front = math.ceil(need_to_add / 1.25)
        pull_from_back = need_to_add - pull_from_front
        contiguous = plain_text.replace(" ", "") or plain_text
        string_to_front = self._cycle_take(contiguous, pull_from_front, front=True)
        string_to_back = self._cycle_take(contiguous, pull_from_back, front=False)

        fragments_front = f"{self._encrypt_segments(string_to_front[::-1])}." if string_to_front else ""
        fragments_back = f".{self._encrypt_segments(string_to_back)}" if string_to_back else ""
        core = self._encrypt_segments(plain_text)
        return f"{fragments_front}{core}{fragments_back}"

    def decrypt_string(self, cipher_text: str) -> str:
        if not cipher_text or cipher_text.isspace():
            return ""
        if "." in cipher_text:
            parts = cipher_text.split(".")
            if len(parts) > 2:
                cipher_text = parts[1]
        return self._decrypt_segments(cipher_text)

    # -------------------------
    # Validation
    # -------------------------

    @staticmethod
    def _validate_alphabet(alphabet: str) -> List[str]:
        if "." in alphabet:
            raise ValueError("Alphabet must not contain '.'")

        seen: set[str] = set()
        unique: List[str] = []
        for ch in alphabet:
            if ch in seen:
                raise ValueError(f"Duplicate character '{ch}' in provided alphabet.")
            seen.add(ch)
            unique.append(ch)

        # Stricter rule (to mirror C# tests if desired)
        if len(unique) < 3:
            raise ValueError("Alphabet must contain at least 3 unique characters")

        return unique

    @staticmethod
    def _validate_key(key: str, alphabet_list: List[str]) -> None:
        if len(key) < 3:
            raise ValueError("Key must be at least 3 characters long")
        alpha_set = set(alphabet_list)
        for ch in key:
            if ch not in alpha_set:
                raise ValueError(f"Alphabet does not contain the character '{ch}' supplied in the key.")

    # -------------------------
    # Segment ops
    # -------------------------

    @staticmethod
    def _cycle_take(source: str, count: int, front: bool) -> str:
        if count <= 0 or not source:
            return ""
        result: List[str] = []
        length = len(source)
        idx = 0
        while len(result) < count:
            result.append(source[idx % length] if front else source[-1 - (idx % length)])
            idx += 1
        return "".join(result)

    def _encrypt_segments(self, text: str) -> str:
        return " ".join(self._encrypt_word(word) if word else "" for word in text.split(" "))

    def _decrypt_segments(self, text: str) -> str:
        return " ".join(self._decrypt_word(word) if word else "" for word in text.split(" "))

    # -------------------------
    # Vigenère-style per-word ops (over alphabet-only encoding)
    # -------------------------

    def _encrypt_word(self, word: str) -> str:
        segment_chars = self._to_alphabet_char_list(word)
        key_chars = self._get_key(segment_chars)
        encrypted = [self._shift_positive(kc, sc) for kc, sc in zip(key_chars, segment_chars)]
        return "".join(encrypted)

    def _decrypt_word(self, word: str) -> str:
        segment_chars = list(word)
        key_chars = self._get_key(segment_chars)
        decrypted = [self._shift_negative(kc, sc) for kc, sc in zip(key_chars, segment_chars)]
        return self._from_alphabet_char_list(decrypted)

    def _shift_positive(self, key_char: str, text_char: str) -> str:
        key_pos = self._alphabet_position_map.get(key_char)
        text_pos = self._alphabet_position_map.get(text_char)
        if key_pos is None or text_pos is None:
            return text_char  # should not occur with alphabet-only input
        return self._alphabet[(key_pos + text_pos) % self._alphabet_length]

    def _shift_negative(self, key_char: str, text_char: str) -> str:
        key_pos = self._alphabet_position_map.get(key_char)
        text_pos = self._alphabet_position_map.get(text_char)
        if key_pos is None or text_pos is None:
            return text_char  # should not occur with alphabet-only input
        return self._alphabet[(text_pos - key_pos + self._alphabet_length) % self._alphabet_length]

    def _get_key(self, segment: List[str]) -> List[str]:
        if not segment:
            return []
        key = list(self._key_chars)
        while len(key) < len(segment):
            key.extend(self._key_chars)
        return key[: len(segment)]

    # -------------------------
    # Alphabet-only Base-N codec
    # -------------------------

    def _bytes_to_alphabet(self, data: bytes) -> str:
        if not data:
            return ""

        # Count leading zero bytes
        zero_count = 0
        for b in data:
            if b == 0:
                zero_count += 1
            else:
                break

        # Convert to big integer
        value = int.from_bytes(data, byteorder="big", signed=False)
        base = self._alphabet_length

        if value == 0:
            # represent at least one zero digit, but keep exact leading zero count
            return self._alphabet[0] * max(1, zero_count)

        digits: List[str] = []
        while value > 0:
            value, rem = divmod(value, base)
            digits.append(self._alphabet[rem])

        return (self._alphabet[0] * zero_count) + "".join(reversed(digits))

    def _alphabet_to_bytes(self, text: str) -> bytes:
        if text == "":
            return b""

        # Count and strip prefix zeros represented by alphabet[0]
        zero_char = self._alphabet[0]
        zero_prefix = 0
        for ch in text:
            if ch == zero_char:
                zero_prefix += 1
            else:
                break

        payload = text[zero_prefix:]
        base = self._alphabet_length

        # Validate all chars are in alphabet and build integer value
        value = 0
        for ch in payload:
            digit = self._alphabet_position_map.get(ch)
            if digit is None:
                raise ValueError(f"Cipher text contains character '{ch}' not in the alphabet.")
            value = value * base + digit

        # Convert integer value to bytes (big-endian)
        core = b"" if value == 0 else value.to_bytes((value.bit_length() + 7) // 8, byteorder="big")

        # Restore leading zero bytes
        return (b"\x00" * zero_prefix) + core

    def _to_alphabet_char_list(self, text: str) -> List[str]:
        if text is None:
            raise ValueError("text cannot be None")
        if text == "":
            return []
        data = text.encode("utf-8")
        encoded = self._bytes_to_alphabet(data)
        return list(encoded)

    def _from_alphabet_char_list(self, chars: List[str]) -> str:
        if not chars:
            return ""
        encoded = "".join(chars)
        data = self._alphabet_to_bytes(encoded)
        return data.decode("utf-8")
