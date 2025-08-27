import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from substitutionciphers import Griffinere


def test_encrypt_and_decrypt_roundtrip():
    key = "N3bhd1u6gh6Uh88H083envHwuUSec72i"
    plaintext = "This is a test of the encryption."
    cipher = Griffinere(key)

    encrypted = cipher.encrypt_string(plaintext)
    decrypted = cipher.decrypt_string(encrypted)

    assert decrypted == plaintext


def test_different_inputs_produce_different_ciphertexts_same_key():
    key = "emz"
    cipher = Griffinere(key)

    encrypted1 = cipher.encrypt_string("Test")
    encrypted2 = cipher.encrypt_string("Text")

    assert encrypted1 != encrypted2


def test_encrypt_and_decrypt_with_custom_alphabet():
    key = "N3bhd1u6gh6Uh88H083envHwuUSec72i"
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    plaintext = "Hello World 123!"
    cipher = Griffinere(key, alphabet)

    encrypted = cipher.encrypt_string(plaintext)
    decrypted = cipher.decrypt_string(encrypted)

    assert decrypted == plaintext


def test_encrypt_string_with_minimum_length():
    key = "N3bhd1u6gh6Uh88H083envHwuUSec72i"
    plaintext = "Short text"
    cipher = Griffinere(key)

    encrypted = cipher.encrypt_string(plaintext, 64)

    assert len(encrypted) >= 64


def test_encrypt_string_with_empty_text_returns_empty():
    cipher = Griffinere("VkiKMyvu7PT3UV08xZr9X1AA5WiZDzDm")
    assert cipher.encrypt_string("") == ""


def test_really_long_key_and_message_roundtrip():
    long_key = (
        "LEWQcmPaCv9b8HNHJQFuqxDRDCJnQbcXmhQR3wwTuFhSPRUGBSJnj2GrTBSKj3tJ"
        "TnnSrVC57DHhnik7EUVL8427EQRM6KHxJWenq1Jiy6qzRDchQt5B57izp744yZ0U"
        "tK5hngr9cq8kYDJnctwCc3TMk5awiw2HrhwyunyF3hEPk5bfhGmWZE61reeaC7Sw"
        "H2iRZF9KYdHEwLQ8u1gV72KfPhMLvtca78ff4FcY7W5GeNZbMySUhU4GytTzU4PE"
        "HwtkQjRgcAqb7yxjaZT787t0wPZjTiyvdmVCreNm0C7exCFXpR6a4NC7QBQgimCa"
        "SWyj1cKZ9xTTML7Wrm6xZD0v5vHSiVKmN79tUpkPPD6TuV73RaTnPcHzqT8Ypnuj"
        "GtJ1jqvGVT6dRdLtbATth1wtLcmnMx5Mc0jLbp6hKicYjVEu7BJyv2mxYcaeyWQv"
        "Xmj81zPEdnJ3wFz4ngXmT1XiRZwucAt2HMpxq3QaRaNGdA1y759dZqhueFbZn8G4"
    )
    original_text = (
        "ikdbr10dbLGm7xtMLkgVhBYVjmkrfAmARyNJXLLbUmvVSTnLMyFWw2vk4tZippWW"
        "JGJwhUq9dK6aD5FNJHyje4yzCTiMqjJ26wttnxSbgbNpXAuXKFUECNzDwFj5Dcf1"
        "JhqjeA9X6bfTBjY975jSYqrNNje1u1tBNTVjwq3qeMtWVFz9Bj2PxZhWuU99K1R8"
        "tedU48uRzjJWdvd18ZSVbwyrTMbGn77FPDAXQirbHiKwcwqXemMVq6tyec7Yc986"
        "KNVixV93Da4Z2jS3ERN66WHjhVwMm5yyb9KN81eiCNYWfJZdyp6mBAX2dNuNeBLQ"
        "r4xP5LNdAFVWg2nn42t9aJNGh1Ep0yr1cGLBcYNXgMwPMqBtJnSLFphhi82zM3Yh"
        "SeTLbSNchLzjJXu0A5ZhHqddPWc5BmnxtDeZ5tw6uTSy76au4MdTTqR3HcXeAVPu"
        "E9fxWSDwxEvh7gRCUBC3bkn7rdUtH8fRJFNLdyYNrNN2SM6C66rdHrhg71d6rGuG"
    )
    cipher = Griffinere(long_key)

    encrypted = cipher.encrypt_string(original_text)
    decrypted = cipher.decrypt_string(encrypted)

    assert decrypted == original_text


def test_really_long_key_with_custom_alphabet_roundtrip():
    long_key = (
        "a{D{BhT(e&V{4zzpQ=Mjw(Hv5epZt;#wf,A!nNTbeMbdA2x%?NwD3kJ@@$)]/*-q/"
        "5x3)/T=_JTzRY$4(ggH!d45CK9R8Vm+y&i8N_Ki+PZ4DA[Cj[fxZ02w%:MV"
    )
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!\"#$%&'()*+,-/:;<=>?@[]^_`{|}~"
    cipher = Griffinere(long_key, alphabet)

    original_text = "Testing encryption."
    encrypted = cipher.encrypt_string(original_text)
    decrypted = cipher.decrypt_string(encrypted)

    assert decrypted == original_text


def test_roundtrip_with_escaped_characters():
    cipher = Griffinere("EuMchtXtJFKhA5H8fGduYPXQEcZJKEAe")
    original_text = "Testing\nSpecial\tCharacters"

    encrypted = cipher.encrypt_string(original_text)
    decrypted = cipher.decrypt_string(encrypted)

    assert decrypted == original_text


def test_roundtrip_with_multiple_spaces():
    cipher = Griffinere("dHiNt8C8JY1RhZ26mtYCHByr0WzzfTLm")
    original_text = "Testing  Double   Triple Space"

    encrypted = cipher.encrypt_string(original_text)
    decrypted = cipher.decrypt_string(encrypted)

    assert decrypted == original_text


def test_numeric_alphabet_includes_digits_case1():
    alphabet = "123"
    key = "123"
    cipher = Griffinere(key, alphabet)

    encrypted = cipher.encrypt_string("The sunset looks lovely.")
    assert "1" in encrypted


def test_numeric_alphabet_includes_digits_case2():
    alphabet = "abcdefg123456"
    key = "123"
    cipher = Griffinere(key, alphabet)

    encrypted = cipher.encrypt_string("The sunset looks lovely.")
    assert "3" in encrypted


def test_constructor_with_invalid_alphabet_should_throw():
    invalid_alphabet = "abc.defghijklmf"  # contains '.'
    key = "A39a3hiirMFAafY1iRBucZxY86AzCeMZ"
    with pytest.raises(ValueError) as exc:
        Griffinere(key, invalid_alphabet)
    assert "must not contain '.'" in str(exc.value)


def test_constructor_with_duplicate_alphabet_chars_should_throw():
    invalid_alphabet = "aabcdefg"  # duplicate 'a'
    key = "abcdefg"
    with pytest.raises(ValueError) as exc:
        Griffinere(key, invalid_alphabet)
    assert "Duplicate character" in str(exc.value)


def test_constructor_with_too_short_alphabet_should_throw():
    invalid_alphabet = "a"  # fewer than 3 unique characters
    key = "a"
    with pytest.raises(ValueError) as exc:
        Griffinere(key, invalid_alphabet)
    assert "at least 3 unique characters" in str(exc.value)


def test_constructor_with_too_short_key_should_throw():
    alphabet = "abcdefghi123"
    invalid_key = "1"
    with pytest.raises(ValueError) as exc:
        Griffinere(invalid_key, alphabet)
    assert "Key must be at least 3 characters long" in str(exc.value)


def test_decrypt_string_with_dot_prefix_still_returns_plaintext():
    key = "dShHPpUQTihcn7ju1wjYTAD1dvbrPKdT"
    plain_text = ".Padding test case."
    cipher = Griffinere(key)

    encrypted = cipher.encrypt_string(plain_text, 64)
    decrypted = cipher.decrypt_string(encrypted)

    assert decrypted == plain_text


def test_encrypt_string_with_invalid_minimum_length_throws():
    key = "dShHPpUQTihcn7ju1wjYTAD1dvbrPKdT"
    cipher = Griffinere(key)
    with pytest.raises(ValueError):
        cipher.encrypt_string("EncryptWithMinLength", 0)
