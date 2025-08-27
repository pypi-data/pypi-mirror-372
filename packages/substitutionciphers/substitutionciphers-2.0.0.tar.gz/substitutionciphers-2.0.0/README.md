# Griffinere Cipher 🔐 — Python Edition

The **Griffinere** cipher is a reversible, Base‑64‑normalised encryption algorithm implemented in pure **Python**.
Inspired by the classic Vigenère cipher, it adds:

-   **Configurable alphabets** (use any character set you like)
-   **Input validation** for safer usage
-   **Padding‑based length enforcement** so encrypted strings meet a minimum length

---

## 📦 Installation

```bash
pip install substitutionciphers
```

In your code:

```python
from substitutionciphers import Griffinere
```

---

## ✨ Features

-   🔐 Encrypts & decrypts alphanumeric or **custom‑alphabet** strings
-   🧩 Define your **own alphabet** (emoji? Cyrillic? go ahead!)
-   📏 Optional **minimum‑length** padding for fixed‑width ciphertext
-   ✅ Strong validation of both alphabet and key integrity
-   🧪 Unit‑tested with **pytest**

---

## 🧰 Usage

### 1 Create a cipher

#### 1.1 Default alphabet

```python
key = "YourSecureKey"
cipher = Griffinere(key)
```

The built‑in alphabet is:

```
A‑Z  a‑z  0‑9
```

#### 1.2 Custom alphabet

```python
custom_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ12345"
key = "YOURKEY"
cipher = Griffinere(key, custom_alphabet)
```

##### Alphabet rules

1. **Must not contain `.`** (dot)
2. **All characters must be unique**
3. **Every character in the key must appear in the alphabet**

---

### 2 Encrypt & decrypt

#### 2.1 Encrypt a string

```python
plain_text = "Hello World 123"
encrypted = cipher.encrypt_string(plain_text)
# e.g. 'LUKsbK8 OK9ybKJ FC3z'
```

#### 2.2 Encrypt with a minimum length

```python
encrypted = cipher.encrypt_string(plain_text, minimum_response_length=24)
# e.g. 'cm9JbAxsIJg.LUKsbK8 OK9ybKJ FC3z.Fw'
```

#### 3.1 Decrypt

```python
decrypted = cipher.decrypt_string(encrypted)
assert decrypted == plain_text
```

---

## ⚠️ Exceptions & validation

| Condition                                       | Exception    |
| ----------------------------------------------- | ------------ |
| Alphabet contains `.`                           | `ValueError` |
| Duplicate characters in alphabet                | `ValueError` |
| Alphabet is fewer than 3 characters long        | `ValueError` |
| Key is fewer than 3 characters long             | `ValueError` |
| Key contains characters not present in alphabet | `ValueError` |
| `minimum_response_length` < 1                   | `ValueError` |

---

## 📄 License

MIT License © 2025 Riley Griffin
